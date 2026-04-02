"""
MCP Client: Manages connections to MCP servers via subprocess
Handles tool invocation and error management
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ToolResult:
    """Result from MCP tool invocation"""
    status: str  # "success" or "error"
    data: dict
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == "success"


class MCPClientConnection:
    """Manages a single MCP server connection via stdio"""

    def __init__(self, server_key: str, script_path: Path):
        self.server_key = server_key
        self.script_path = script_path
        self.process = None
        self.is_connected = False

    async def connect(self):
        """Establish subprocess connection to MCP server"""
        if self.is_connected:
            return

        try:
            logger.info(f"Connecting to {self.server_key} MCP server: {self.script_path}")

            # Spawn subprocess for MCP server
            self.process = await asyncio.create_subprocess_exec(
                "python3",
                str(self.script_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            self.is_connected = True
            logger.info(f"Connected to {self.server_key} MCP server")

        except Exception as e:
            logger.error(f"Failed to connect to {self.server_key}: {e}")
            self.is_connected = False
            raise

    async def disconnect(self):
        """Close subprocess connection"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error disconnecting from {self.server_key}: {e}")
            finally:
                self.is_connected = False

    async def call_tool(self, tool_name: str, args: dict) -> ToolResult:
        """Call a tool on the MCP server"""
        if not self.is_connected:
            await self.connect()

        try:
            # Prepare MCP request (simplified; actual protocol is more complex)
            # For now, we'll use a simple JSON-based protocol
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": args
                }
            }

            # Send request
            self.process.stdin.write((json.dumps(request) + "\n").encode())
            await self.process.stdin.drain()

            # Read response (with timeout)
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=settings.MCP_TOOL_TIMEOUT
            )

            if not response_line:
                return ToolResult(status="error", data={}, error="No response from server")

            response = json.loads(response_line.decode().strip())

            # Extract result from response
            if "error" in response:
                return ToolResult(status="error", data=response.get("error", {}), error=str(response["error"]))

            # Assuming response format: {"result": {...}}
            result_data = response.get("result", {})
            status = result_data.get("status", "success")

            return ToolResult(status=status, data=result_data)

        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {tool_name} on {self.server_key}")
            return ToolResult(status="error", data={}, error="Tool call timeout")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from {self.server_key}: {e}")
            return ToolResult(status="error", data={}, error="Invalid JSON response")
        except Exception as e:
            logger.error(f"Error calling {tool_name} on {self.server_key}: {e}")
            return ToolResult(status="error", data={}, error=str(e))


class MCPClientPool:
    """Manages connections to all MCP servers"""

    def __init__(self):
        self.connections: dict[str, MCPClientConnection] = {}
        self._init_servers()

    def _init_servers(self):
        """Initialize all server connections"""
        servers = {
            "ppt": settings.PPT_SERVER_SCRIPT,
            "web_search": settings.WEB_SEARCH_SERVER_SCRIPT,
            "filesystem": settings.FILESYSTEM_SERVER_SCRIPT,
            "theme": settings.THEME_SERVER_SCRIPT
        }

        for key, path in servers.items():
            self.connections[key] = MCPClientConnection(key, path)

    async def connect_all(self):
        """Connect to all MCP servers"""
        tasks = [conn.connect() for conn in self.connections.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Log status
        connected = sum(1 for conn in self.connections.values() if conn.is_connected)
        logger.info(f"Connected to {connected}/{len(self.connections)} MCP servers")

    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        tasks = [conn.disconnect() for conn in self.connections.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Disconnected from all MCP servers")

    async def call_tool(self, server_key: str, tool_name: str, args: dict) -> ToolResult:
        """Call a tool on a specific server"""
        if server_key not in self.connections:
            return ToolResult(status="error", data={}, error=f"Unknown server: {server_key}")

        connection = self.connections[server_key]
        return await connection.call_tool(tool_name, args)


# Singleton instance
_mcp_pool: Optional[MCPClientPool] = None


async def get_mcp_pool() -> MCPClientPool:
    """Get or create MCP client pool"""
    global _mcp_pool
    if _mcp_pool is None:
        _mcp_pool = MCPClientPool()
        await _mcp_pool.connect_all()
    return _mcp_pool


async def shutdown_mcp():
    """Shutdown MCP connections"""
    global _mcp_pool
    if _mcp_pool:
        await _mcp_pool.disconnect_all()
        _mcp_pool = None
