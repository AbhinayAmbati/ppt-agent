#!/usr/bin/env python3
"""
MCP Server Configuration
Defines all MCP servers and their connection parameters
"""

import os
from pathlib import Path

# Base directory for MCP servers
MCP_SERVERS_DIR = Path(__file__).parent / "servers"

# Server definitions
MCP_SERVERS = {
    "ppt_server": {
        "name": "PPT Server",
        "script": MCP_SERVERS_DIR / "1.ppt_server.py",
        "description": "Core PowerPoint creation and manipulation",
        "type": "stdio",
        "tools": [
            "create_presentation",
            "add_slide",
            "write_text_to_slide",
            "add_image_placeholder",
            "save_presentation",
            "get_presentation_info"
        ]
    },
    "web_search_server": {
        "name": "Web Search Server",
        "script": MCP_SERVERS_DIR / "2.web_search_server.py",
        "description": "Web search and content fetching",
        "type": "stdio",
        "tools": [
            "search_topic",
            "fetch_page_summary"
        ]
    },
    "filesystem_server": {
        "name": "Filesystem Server",
        "script": MCP_SERVERS_DIR / "3.filesystem_server.py",
        "description": "File I/O and output management",
        "type": "stdio",
        "tools": [
            "save_file",
            "list_output_files",
            "get_file_path",
            "delete_file"
        ]
    },
    "theme_server": {
        "name": "Theme Server",
        "script": MCP_SERVERS_DIR / "4.theme_server.py",
        "description": "Presentation theming and styling",
        "type": "stdio",
        "tools": [
            "apply_theme",
            "set_color_scheme",
            "set_font_style",
            "get_available_themes"
        ]
    }
}

# All available tools across all servers
ALL_TOOLS = {}
for server_key, server_config in MCP_SERVERS.items():
    for tool in server_config["tools"]:
        ALL_TOOLS[tool] = server_key


def get_server_config(server_name: str) -> dict:
    """Get configuration for a specific server"""
    return MCP_SERVERS.get(server_name)


def get_tool_server(tool_name: str) -> str:
    """Get which server provides a specific tool"""
    return ALL_TOOLS.get(tool_name)


def verify_servers_exist() -> bool:
    """Verify all server scripts exist"""
    for server_key, config in MCP_SERVERS.items():
        script_path = config["script"]
        if not script_path.exists():
            print(f"ERROR: {server_key} script not found at {script_path}")
            return False
    return True


if __name__ == "__main__":
    print("MCP Server Configuration")
    print("======================")

    if verify_servers_exist():
        print("\nAll servers found!\n")
        for server_key, config in MCP_SERVERS.items():
            print(f"{config['name']}:")
            print(f"  Script: {config['script']}")
            print(f"  Tools: {', '.join(config['tools'])}")
            print()
    else:
        print("\nSome servers are missing!\n")
        exit(1)
