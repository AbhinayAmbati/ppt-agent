#!/usr/bin/env python3
import json
import os
from pathlib import Path
import mcp.server.stdio
from mcp.types import Tool, TextContent

OUTPUT_DIR = "output"

def ensure_output_dir():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

async def save_file(file_path: str, content: str) -> dict:
    try:
        ensure_output_dir()
        full_path = Path(OUTPUT_DIR) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return {
            "status": "success",
            "message": f"File saved to {full_path}",
            "file_path": str(full_path),
            "size": len(content)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def list_output_files() -> dict:
    try:
        ensure_output_dir()
        files = []
        for root, dirs, filenames in os.walk(OUTPUT_DIR):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append({
                    "name": filename,
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                })
        return {
            "status": "success",
            "files_count": len(files),
            "files": files
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def get_file_path(file_name: str) -> dict:
    try:
        ensure_output_dir()
        full_path = Path(OUTPUT_DIR) / file_name
        return {
            "status": "success",
            "file_name": file_name,
            "full_path": str(full_path.absolute()),
            "exists": full_path.exists()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def delete_file(file_path: str) -> dict:
    try:
        full_path = Path(OUTPUT_DIR) / file_path
        if full_path.exists():
            full_path.unlink()
            return {
                "status": "success",
                "message": f"File deleted: {full_path}"
            }
        else:
            return {"status": "error", "message": "File not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def main():
    server = mcp.server.stdio.StdioServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="save_file",
                description="Save content to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path relative to output dir"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    "required": ["file_path", "content"]
                }
            ),
            Tool(
                name="list_output_files",
                description="List all files in output directory",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_file_path",
                description="Get full path of a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name or relative path"}
                    },
                    "required": ["file_name"]
                }
            ),
            Tool(
                name="delete_file",
                description="Delete a file from output directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path relative to output dir"}
                    },
                    "required": ["file_path"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "save_file":
            result = await save_file(arguments["file_path"], arguments["content"])
        elif name == "list_output_files":
            result = await list_output_files()
        elif name == "get_file_path":
            result = await get_file_path(arguments["file_name"])
        elif name == "delete_file":
            result = await delete_file(arguments["file_path"])
        else:
            result = {"status": "error", "message": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result))]

    async with server:
        await server.wait_for_shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
