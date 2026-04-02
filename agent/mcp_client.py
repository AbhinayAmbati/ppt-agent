"""
MCP Client Manager
Handles connections to all 4 MCP servers via stdio
Includes error handling and retry logic
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPClient:
    """Manages MCP server connections"""
    
    def __init__(self):
        self.servers = {}
        self.processes = {}
        self.mcp_servers_path = Path(__file__).parent.parent / "mcp" / "servers"
        
    async def start_server(self, server_name: str, script_path: str) -> bool:
        """Start an MCP server process"""
        try:
            # Get full path to server script
            server_script = self.mcp_servers_path / script_path
            
            if not server_script.exists():
                logger.error(f"Server script not found: {server_script}")
                return False
            
            # Start subprocess
            process = subprocess.Popen(
                ["python3", str(server_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.processes[server_name] = process
            logger.info(f"Started MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server {server_name}: {e}")
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server process"""
        try:
            if server_name in self.processes:
                process = self.processes[server_name]
                process.terminate()
                process.wait(timeout=5)
                del self.processes[server_name]
                logger.info(f"Stopped MCP server: {server_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to stop server {server_name}: {e}")
            return False
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any], 
                       retry_count: int = 3) -> Optional[Dict[str, Any]]:
        """
        Call a tool on an MCP server with retry logic
        """
        for attempt in range(retry_count):
            try:
                if server_name not in self.processes or self.processes[server_name].poll() is not None:
                    await self.start_server(server_name, f"{self._get_script_name(server_name)}")
                
                process = self.processes.get(server_name)
                if not process:
                    logger.error(f"Server {server_name} not available")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(1)
                        continue
                    return None
                
                # Send tool call request
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                process.stdin.write(json.dumps(request) + "\n")
                process.stdin.flush()
                
                # Read response with timeout
                loop = asyncio.get_event_loop()
                response_line = await asyncio.wait_for(
                    loop.run_in_executor(None, process.stdout.readline),
                    timeout=30
                )
                
                if response_line:
                    response = json.loads(response_line)
                    logger.info(f"Tool {tool_name} on {server_name} executed successfully")
                    return response
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout calling {tool_name} on {server_name} (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error calling {tool_name} on {server_name}: {e} (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2)
        
        logger.error(f"Failed to call {tool_name} on {server_name} after {retry_count} attempts")
        return None
    
    def _get_script_name(self, server_name: str) -> str:
        """Map server name to script file"""
        mapping = {
            "ppt_server": "1.ppt_server.py",
            "web_search_server": "2.web_search_server.py",
            "filesystem_server": "3.filesystem_server.py",
            "theme_server": "4.theme_server.py"
        }
        return mapping.get(server_name, "")
    
    async def shutdown(self):
        """Shutdown all servers"""
        for server_name in list(self.processes.keys()):
            await self.stop_server(server_name)

# Global MCP client instance
mcp_client = MCPClient()
