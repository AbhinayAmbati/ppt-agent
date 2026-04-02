#!/usr/bin/env python3
import json
import mcp.server.stdio
from mcp.types import Tool, TextContent

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

async def search_topic(topic: str, max_results: int = 5) -> dict:
    if DDGS is None:
        return {"status": "error", "message": "duckduckgo-search not installed"}
    try:
        ddgs = DDGS()
        results = list(ddgs.text(topic, max_results=max_results))
        return {
            "status": "success",
            "topic": topic,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def fetch_page_summary(url: str) -> dict:
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs[:3]])
        return {
            "status": "success",
            "url": url,
            "summary": text[:500]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def main():
    server = mcp.server.stdio.StdioServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_topic",
                description="Search for a topic using DuckDuckGo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic to search"},
                        "max_results": {"type": "integer", "description": "Max results"}
                    },
                    "required": ["topic"]
                }
            ),
            Tool(
                name="fetch_page_summary",
                description="Fetch and summarize a web page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"}
                    },
                    "required": ["url"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "search_topic":
            result = await search_topic(arguments["topic"], arguments.get("max_results", 5))
        elif name == "fetch_page_summary":
            result = await fetch_page_summary(arguments["url"])
        else:
            result = {"status": "error", "message": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result))]

    async with server:
        await server.wait_for_shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
