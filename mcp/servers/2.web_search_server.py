#!/usr/bin/env python3
"""
Web Search MCP Server - Fixed Version
Uses same binary stdio pattern as ppt_server.
Provides real search results to enrich slide content.
"""

import sys
import json
import asyncio

try:
    from duckduckgo_search import DDGS
    _DDGS_AVAILABLE = True
except ImportError:
    _DDGS_AVAILABLE = False


async def search_topic(query: str, max_results: int = 5) -> dict:
    """Search DuckDuckGo and return title + snippet for each result."""
    if not _DDGS_AVAILABLE:
        return {"status": "error", "message": "duckduckgo-search not installed"}
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":   r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url":     r.get("href", ""),
                })
        return {
            "status":  "success",
            "query":   query,
            "count":   len(results),
            "results": results,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "results": []}


async def fetch_page_summary(url: str) -> dict:
    """Fetch a URL and return the first 500 chars of clean text."""
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:5]).strip()
        return {"status": "success", "url": url, "summary": text[:600]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def call_tool(name: str, arguments: dict) -> dict:
    if name == "search_topic":
        return await search_topic(
            arguments.get("query") or arguments.get("topic", ""),
            arguments.get("max_results", 5),
        )
    elif name == "fetch_page_summary":
        return await fetch_page_summary(arguments["url"])
    else:
        return {"status": "error", "message": f"Unknown tool: {name}"}


async def main():
    stdin  = sys.stdin.buffer
    stdout = sys.stdout.buffer
    while True:
        line = stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line.decode("utf-8").strip())
            if req.get("method") == "tools/call":
                result = await call_tool(
                    req["params"]["name"],
                    req["params"].get("arguments", {}),
                )
            else:
                result = {"status": "error", "message": f"Unknown method: {req.get('method')}"}
        except Exception as e:
            result = {"status": "error", "message": f"Parse error: {e}"}
        stdout.write((json.dumps(result) + "\n").encode("utf-8"))
        stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
