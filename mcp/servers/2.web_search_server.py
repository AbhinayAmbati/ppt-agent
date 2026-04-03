#!/usr/bin/env python3
"""
Web Search MCP Server  (2.web_search_server.py)
================================================
MCP server providing DuckDuckGo text search to the Auto-PPT agent.
Communicates via binary stdio — same transport pattern as 1.ppt_server.py.

Exposed Tools
-------------
search_topic(query, max_results=5)
    Searches DuckDuckGo for `query` and returns up to max_results results.
    Each result contains: title, snippet (body text), url.
    Used by agent_engine Phase 2 to inject real facts into slide bullet points.
    Falls back to {"status": "error", "results": []} on any failure — never crashes.

fetch_page_summary(url)
    Fetches a URL and returns the first ~600 chars of clean paragraph text.
    Useful for deeper fact extraction when search snippets are too brief.

Transport
---------
Binary stdio (sys.stdin.buffer / sys.stdout.buffer).
Request  : {"method": "tools/call", "params": {"name": "...", "arguments": {...}}}
Response : {"status": "success"|"error", ...}

Dependencies
------------
duckduckgo-search>=6.2.0   (pip install duckduckgo-search)
requests                    (for fetch_page_summary)
beautifulsoup4              (for HTML stripping in fetch_page_summary)
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
    """
    Search DuckDuckGo for `query` and return structured results.

    Parameters
    ----------
    query       : search string (e.g. "Distributed Systems CAP Theorem")
    max_results : maximum number of results to return (default 5)

    Returns
    -------
    {
        "status":  "success",
        "query":   str,
        "count":   int,
        "results": [{"title": str, "snippet": str, "url": str}, ...]
    }
    or {"status": "error", "message": str, "results": []} on failure.
    """
    if not _DDGS_AVAILABLE:
        return {"status": "error", "message": "duckduckgo-search not installed", "results": []}
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":   r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url":     r.get("href", ""),
                })
        return {"status": "success", "query": query, "count": len(results), "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e), "results": []}


async def fetch_page_summary(url: str) -> dict:
    """
    Fetch a web page and return the first ~600 characters of clean paragraph text.

    Parameters
    ----------
    url : fully qualified URL to fetch

    Returns
    -------
    {"status": "success", "url": str, "summary": str}
    or {"status": "error", "message": str}
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.content, "html.parser")
        text = " ".join(p.get_text() for p in soup.find_all("p")[:5]).strip()
        return {"status": "success", "url": url, "summary": text[:600]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def call_tool(name: str, arguments: dict) -> dict:
    """Route an MCP tool-call to the appropriate handler."""
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
    """Binary stdio event loop — reads newline-delimited JSON requests, writes JSON responses."""
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
