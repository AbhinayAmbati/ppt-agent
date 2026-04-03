"""
MCP Client Manager - FIXED v2
New fix: stderr is now captured and logged so server crashes are visible.
Also added a startup health-check ping to detect dead servers early.
"""

import asyncio
import json
import sys
import logging
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.mcp_servers_path = Path(__file__).parent.parent / "mcp" / "servers"

    def _get_script_name(self, server_name: str) -> str:
        mapping = {
            "ppt_server":        "1.ppt_server.py",
            "web_search_server": "2.web_search_server.py",
            "filesystem_server": "3.filesystem_server.py",
            "theme_server":      "4.theme_server.py",
        }
        return mapping.get(server_name, "")

    def _get_venv_python(self) -> str:
        """
        Priority order:
        1. mcp/servers/venv  (dedicated MCP venv — has python-pptx, mcp, etc.)
        2. agent/venv
        3. sys.executable fallback
        """
        candidates = [
            self.mcp_servers_path / "venv" / "Scripts" / "python.exe",
            Path(__file__).parent / "venv" / "Scripts" / "python.exe",
        ]
        for p in candidates:
            if p.exists():
                logger.info(f"Using python: {p}")
                return str(p)
        logger.warning(f"No venv found — falling back to {sys.executable}")
        return sys.executable

    def _is_alive(self, server_name: str) -> bool:
        proc = self.processes.get(server_name)
        return proc is not None and proc.poll() is None

    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server — captures stderr so crashes are logged"""
        try:
            script_name = self._get_script_name(server_name)
            if not script_name:
                logger.error(f"Unknown server: {server_name}")
                return False

            server_script = self.mcp_servers_path / script_name
            if not server_script.exists():
                logger.error(f"Server script not found: {server_script}")
                return False

            python_exe = self._get_venv_python()

            process = subprocess.Popen(
                [python_exe, str(server_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,   # capture stderr
                text=False,
                bufsize=0,
            )

            self.processes[server_name] = process

            # Give the process 1 second to start, then check if it already died
            await asyncio.sleep(1.0)
            if process.poll() is not None:
                # Process died on startup — read stderr to show why
                stderr_output = process.stderr.read().decode("utf-8", errors="replace")
                logger.error(
                    f"Server {server_name} died immediately on startup!\n"
                    f"stderr:\n{stderr_output}"
                )
                del self.processes[server_name]
                return False

            logger.info(f"Started MCP server: {server_name} (pid={process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start server {server_name}: {e}")
            return False

    async def _ensure_server(self, server_name: str) -> bool:
        if self._is_alive(server_name):
            return True
        logger.info(f"Server {server_name} not running — starting...")
        return await self.start_server(server_name)

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        retry_count: int = 3,
    ) -> Optional[Dict[str, Any]]:

        for attempt in range(1, retry_count + 1):
            try:
                if not await self._ensure_server(server_name):
                    logger.error(f"Cannot start {server_name} — aborting tool call")
                    return None

                process = self.processes[server_name]

                request = {
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                }
                payload = (json.dumps(request) + "\n").encode("utf-8")
                process.stdin.write(payload)
                process.stdin.flush()

                loop = asyncio.get_event_loop()
                raw_line = await asyncio.wait_for(
                    loop.run_in_executor(None, process.stdout.readline),
                    timeout=30,
                )

                if not raw_line:
                    # Check if process died and grab stderr
                    if process.poll() is not None:
                        stderr_out = process.stderr.read().decode("utf-8", errors="replace")
                        logger.error(f"Server {server_name} crashed during {tool_name}!\nstderr:\n{stderr_out}")
                    raise RuntimeError("Empty response from server")

                response = json.loads(raw_line.decode("utf-8").strip())
                logger.info(f"[{server_name}] {tool_name} → {response.get('status', 'ok')}")
                return response

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on {tool_name}@{server_name} (attempt {attempt}/{retry_count})")
                self._kill(server_name)
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error on {tool_name}@{server_name}: {e} (attempt {attempt}/{retry_count})")
                self._kill(server_name)
                await asyncio.sleep(1)

        logger.error(f"Failed to call {tool_name}@{server_name} after {retry_count} attempts")
        return None

    def _kill(self, server_name: str):
        proc = self.processes.pop(server_name, None)
        if proc:
            try:
                proc.kill()
            except Exception:
                pass

    async def stop_server(self, server_name: str):
        proc = self.processes.pop(server_name, None)
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            logger.info(f"Stopped MCP server: {server_name}")

    async def shutdown(self):
        for name in list(self.processes.keys()):
            await self.stop_server(name)


mcp_client = MCPClient()
