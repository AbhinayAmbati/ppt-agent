# 🔧 MCP Servers - SlideForage Backend Infrastructure

> Four specialized Model Context Protocol (MCP) servers providing distributed, fault-tolerant presentation generation capabilities. Each server handles a specific domain using stdio-based communication.

**Status:** Production Ready | **Version:** 1.0.0 | **Servers:** 4 | **Tools:** 16

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Why MCP Architecture?](#why-mcp-architecture)
3. [Quick Start](#quick-start)
4. [Server Architecture](#server-architecture)
5. [Server Documentation](#server-documentation)
6. [Tool Reference](#tool-reference)
7. [Communication Protocol](#communication-protocol)
8. [Error Handling](#error-handling)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The MCP Servers are the backbone of SlideForage's distributed architecture. Four specialized servers handle different responsibilities:

```
Agent Engine
    ↓
[MCP Client communicates with all 4 servers]
    ↓
┌──────────────────────────────────────────────────┐
│ 4 Specialized MCP Servers Working in Parallel    │
├──────────────────────────────────────────────────┤
│ 1. PPT Server        (6 tools)  - PowerPoint     │
│ 2. Web Search Server (2 tools)  - Web content    │
│ 3. Filesystem Server (4 tools)  - File I/O       │
│ 4. Theme Server      (4 tools)  - Styling        │
└──────────────────────────────────────────────────┘
    ↑                           ↑
    └── Can fail independently, agent continues ──┘
```

**Total:** 4 servers | 16 tools | Clean separation of concerns

---

## 🤔 Why MCP Architecture?

### Benefits of This Design

1. **Separation of Concerns**
   - Each server owns its domain
   - PPT Server stays focused on PowerPoint
   - Web Search Server handles only web operations
   - Filesystem operations isolated
   - Theme management centralized

2. **Fault Isolation**
   - If Web Search fails → Script continues with planned content
   - If Theme fails → Presentation still created (unthemed)
   - If one tool times out → Retry logic kicks in
   - System degrades gracefully, doesn't crash

3. **Scalability**
   - Servers can run on different machines
   - Can scale specific servers independently
   - Future: Support load balancing

4. **Maintainability**
   - Each server is ~500-600 lines
   - Easy to understand and modify
   - Tools are self-contained functions
   - Clear documentation per server

5. **Extensibility**
   - Easy to add new MCP servers
   - Can integrate external services
   - Minimal impact on agent logic

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- MCP servers auto-start when backend runs

### Installation

```bash
cd mcp/servers

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Servers

**Option 1: Manual Start (for testing)**
```bash
# Terminal 1
python 1.ppt_server.py

# Terminal 2
python 2.web_search_server.py

# Terminal 3
python 3.filesystem_server.py

# Terminal 4
python 4.theme_server.py
```

**Option 2: Auto-start (normal operation)**
```bash
# MCP servers auto-start when backend runs
cd ../..
cd agent
python main.py  # MCP servers start automatically
```

### Verify Installation

```bash
# All servers should respond to stdio
# Without starting manually, check backend logs:
cd agent
python main.py

# Look for: "MCP servers initialized successfully"
```

---

## 🏗️ Server Architecture

### Communication Pattern

Each MCP server uses **stdio-based communication** (JSON messages):

```
Agent → MCP Client → Server A (stdio)
                   ├─ Server B (stdio)
                   ├─ Server C (stdio)
                   └─ Server D (stdio)

Example message:
{
  "method": "tools/call",
  "params": {
    "name": "create_presentation",
    "arguments": {"title": "AI", "subtitle": "Overview"}
  }
}

Response:
{
  "content": [{
    "type": "text",
    "text": "Presentation created successfully"
  }]
}
```

### Server Startup Sequence

```
Agent Engine Starts
        ↓
MCP Client initializes
        ↓
Launch 4 subprocesses:
  ├─ Process 1: ppt_server.py (stdio)
  ├─ Process 2: web_search_server.py (stdio)
  ├─ Process 3: filesystem_server.py (stdio)
  └─ Process 4: theme_server.py (stdio)
        ↓
Ping each server (handshake)
        ↓
All servers ready
        ↓
Agent can now make tool calls
```

---

## 📚 Server Documentation

### 1️⃣ PPT Server (1.ppt_server.py)

**Purpose:** PowerPoint creation and manipulation

**Tools:** 6

| Tool | Parameter | Returns | Timeout |
|------|-----------|---------|---------|
| `create_presentation` | title, subtitle | Status | 5s |
| `add_slide` | layout_type | Slide index | 5s |
| `write_text_to_slide` | slide_index, title, content | Status | 10s |
| `add_image_placeholder` | slide_index, text | Status | 5s |
| `save_presentation` | file_path | File path | 5s |
| `get_presentation_info` | - | Slide count | 2s |

**Example Usage:**

```python
# Tool 1: Create presentation
{
  "tool_name": "create_presentation",
  "arguments": {
    "title": "Machine Learning",
    "subtitle": "A Comprehensive Guide"
  }
}
# Response: {"status": "success", "presentation_id": "..."}

# Tool 2: Add slide
{
  "tool_name": "add_slide",
  "arguments": {
    "layout_type": "title_and_content"
  }
}
# Response: {"status": "success", "slide_index": 1}

# Tool 3: Write content
{
  "tool_name": "write_text_to_slide",
  "arguments": {
    "slide_index": 1,
    "title": "Introduction",
    "content": [
      "What is ML?",
      "Why is it important?",
      "Real-world applications"
    ]
  }
}
# Response: {"status": "success"}

# Tool 5: Save file
{
  "tool_name": "save_presentation",
  "arguments": {
    "file_path": "output/presentation_20240405_153042.pptx"
  }
}
# Response: {"status": "success", "file_path": "output/..."}
```

**Dependencies:**
- `python-pptx` - PowerPoint manipulation
- `mcp` - Model Context Protocol

---

### 2️⃣ Web Search Server (2.web_search_server.py)

**Purpose:** Real-time web content for slides

**Tools:** 2

| Tool | Parameter | Returns | Timeout |
|------|-----------|---------|---------|
| `search_topic` | topic, max_results | Web results | 10s |
| `fetch_page_summary` | url | Page summary | 8s |

**Example Usage:**

```python
# Tool 1: Search web
{
  "tool_name": "search_topic",
  "arguments": {
    "topic": "Machine Learning algorithms",
    "max_results": 3
  }
}
# Response: {
#   "results": [
#     {
#       "title": "ML Algorithms Explained",
#       "url": "https://...",
#       "snippet": "Machine learning algorithms are..."
#     },
#     ...
#   ]
# }

# Tool 2: Fetch summary
{
  "tool_name": "fetch_page_summary",
  "arguments": {
    "url": "https://example.com/ml-guide"
  }
}
# Response: {
#   "summary": "This guide covers supervised learning...",
#   "title": "Complete ML Guide"
# }
```

**Features:**
- Uses DuckDuckGo (no API key needed)
- Gracefully handles failed searches
- Returns structured results
- Timeout protection

**Dependencies:**
- `duckduckgo-search` - Web search
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `mcp` - Model Context Protocol

---

### 3️⃣ Filesystem Server (3.filesystem_server.py)

**Purpose:** File I/O operations

**Tools:** 4

| Tool | Parameter | Returns | Timeout |
|------|-----------|---------|---------|
| `save_file` | file_path, content | Status | 5s |
| `list_output_files` | - | File list | 3s |
| `get_file_path` | file_name | Absolute path | 2s |
| `delete_file` | file_path | Status | 3s |

**Example Usage:**

```python
# Tool 1: Save file
{
  "tool_name": "save_file",
  "arguments": {
    "file_path": "output/report.txt",
    "content": "Generated report content..."
  }
}
# Response: {"status": "success", "path": "/full/path/..."}

# Tool 2: List files
{
  "tool_name": "list_output_files",
  "arguments": {}
}
# Response: {
#   "files": [
#     {"name": "presentation_20240405_153042.pptx", "size": 2500000},
#     {"name": "presentation_20240404_120000.pptx", "size": 2400000}
#   ]
# }

# Tool 3: Get file path
{
  "tool_name": "get_file_path",
  "arguments": {
    "file_name": "presentation_20240405_153042.pptx"
  }
}
# Response: {"path": "/full/absolute/path/presentation_20240405_153042.pptx"}

# Tool 4: Delete file
{
  "tool_name": "delete_file",
  "arguments": {
    "file_path": "output/old_presentation.pptx"
  }
}
# Response: {"status": "success"}
```

**Features:**
- All operations go through this server
- PPT Server doesn't touch filesystem directly
- Clean separation of concerns
- Secure file access control

**Dependencies:**
- Standard library only (os, pathlib)
- `mcp` - Model Context Protocol

---

### 4️⃣ Theme Server (4.theme_server.py)

**Purpose:** Presentation styling and theming

**Tools:** 4

| Tool | Parameter | Returns | Timeout |
|------|-----------|---------|---------|
| `apply_theme` | theme_name | Status | 5s |
| `set_color_scheme` | primary, secondary, accent | Status | 5s |
| `set_font_style` | font_name, font_size | Status | 3s |
| `get_available_themes` | - | Theme list | 2s |

**Example Usage:**

```python
# Tool 1: Apply theme
{
  "tool_name": "apply_theme",
  "arguments": {
    "theme_name": "ocean"
  }
}
# Response: {"status": "success", "theme": "ocean"}

# Available themes:
# - "default" - Professional blue
# - "ocean" - Cool blue/teal
# - "forest" - Natural green
# - "sunset" - Warm orange
# - "midnight" - Dark blue

# Tool 2: Set custom colors
{
  "tool_name": "set_color_scheme",
  "arguments": {
    "primary": "#0077B6",
    "secondary": "#8CC7E0",
    "accent": "#FFB700"
  }
}
# Response: {"status": "success"}

# Tool 3: Set font style
{
  "tool_name": "set_font_style",
  "arguments": {
    "font_name": "helvetica",
    "font_size": 12
  }
}
# Response: {"status": "success"}

# Tool 4: Get available themes
{
  "tool_name": "get_available_themes",
  "arguments": {}
}
# Response: {
#   "themes": ["default", "ocean", "forest", "sunset", "midnight"],
#   "custom_themes": []
# }
```

**Features:**
- 5 built-in professional themes
- Custom color scheme support
- Font customization
- Theme preview capability

**Dependencies:**
- `python-pptx` - PowerPoint styling
- `mcp` - Model Context Protocol

---

## 🔧 Tool Reference

### Quick Lookup Table

| Server | Tool | Purpose | Inputs | Outputs |
|--------|------|---------|--------|---------|
| **PPT** | create_presentation | Initialize .pptx | title, subtitle | status |
| **PPT** | add_slide | Add blank slide | layout_type | slide_index |
| **PPT** | write_text_to_slide | Add content | slide_idx, title, bullets | status |
| **PPT** | add_image_placeholder | Add image | slide_idx, text | status |
| **PPT** | save_presentation | Save to disk | file_path | file_path |
| **PPT** | get_presentation_info | Get metadata | - | slide_count |
| **Search** | search_topic | Web search | topic, max_results | results |
| **Search** | fetch_page_summary | Extract summary | url | summary |
| **Filesystem** | save_file | Write file | path, content | status |
| **Filesystem** | list_output_files | List files | - | files |
| **Filesystem** | get_file_path | Resolve path | file_name | path |
| **Filesystem** | delete_file | Remove file | file_path | status |
| **Theme** | apply_theme | Use theme | theme_name | status |
| **Theme** | set_color_scheme | Custom colors | primary, secondary, accent | status |
| **Theme** | set_font_style | Change fonts | font_name, size | status |
| **Theme** | get_available_themes | List themes | - | themes |

---

## 📡 Communication Protocol

### MCP Message Format

**Request (Agent → Server):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

**Response (Server → Agent):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool executed successfully"
      }
    ]
  }
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal server error",
    "data": {
      "details": "Detailed error message..."
    }
  }
}
```

### Execution Order in Agent

```
Phase 1: PLANNING
  (No MCP calls)

Phase 2: CREATE
  └─ PPT Server: create_presentation()

Phase 3: BUILD (for each slide)
  ├─ Web Search Server: search_topic() [optional]
  ├─ PPT Server: add_slide()
  └─ PPT Server: write_text_to_slide()

Phase 4: APPLY THEME
  └─ Theme Server: apply_theme()

Phase 5: SAVE
  └─ PPT Server: save_presentation()
```

---

## 🛡️ Error Handling

### Server Error Scenarios

```
Scenario 1: Web Search Fails
  ├─ Agent calls: search_topic("AI")
  ├─ Server times out (>10s)
  ├─ MCP Client retries (×3 with backoff)
  ├─ All retries fail
  └─ Agent continues with planned content

Scenario 2: File Save Fails
  ├─ Agent calls: save_presentation(path)
  ├─ Permission denied error
  ├─ MCP Client retries (×3)
  ├─ Still fails
  └─ Agent returns error to user

Scenario 3: Server Crashes
  ├─ PPT Server crashes mid-operation
  ├─ MCP Client detects no response
  ├─ Retry logic exhausted
  ├─ Agent logs error
  └─ Agent tries to recover from backup

Scenario 4: Timeout During Build
  ├─ Building slide 3 of 5
  ├─ write_text_to_slide() times out
  ├─ Retry × 3 with backoff
  ├─ Still fails
  ├─ Agent skips this slide
  └─ Continues with slides 4-5
```

### Retry Strategy

```
Initial Call → Timeout/Error
  ↓
Wait 1 second
  ↓
Retry 1 → Timeout/Error
  ↓
Wait 2 seconds
  ↓
Retry 2 → Timeout/Error
  ↓
Wait 2 seconds
  ↓
Retry 3 → Timeout/Error
  ↓
Return Error to Agent
  ↓
Agent decides whether to continue or fail
```

**Configuration:**
- Max retries: 3
- Initial backoff: 1 second
- Max backoff: 2 seconds
- Per-tool timeout: 10 seconds (configurable)

---

## 🚀 Deployment

### Single Machine

```bash
# On production server
cd mcp/servers

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run via backend (auto-start)
cd ../../agent
python main.py
```

### Multiple Machines

```bash
# Machine 1: Backend + PPT/Theme Servers
cd mcp/servers
python 1.ppt_server.py &
python 4.theme_server.py &
cd ../../agent
python main.py

# Machine 2: Web Search Server
cd mcp/servers
python 2.web_search_server.py

# Machine 3: Filesystem Server
cd mcp/servers
python 3.filesystem_server.py
```

### Docker Deployment

**Dockerfile (all servers):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY mcp/servers/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp/servers/ .

# Run backend which auto-starts servers
COPY agent/requirements.txt ../agent/
RUN pip install --no-cache-dir -r ../agent/requirements.txt

COPY agent/ ../agent/

WORKDIR /app/../agent

CMD ["python", "main.py"]
```

### Kubernetes Deployment

Each server as a separate deployment:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slideforge-ppt-server
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: ppt
        image: slideforge-mcp:latest
        command: ["python", "1.ppt_server.py"]
        ports:
        - containerPort: 9001

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slideforge-web-search-server
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: search
        image: slideforge-mcp:latest
        command: ["python", "2.web_search_server.py"]
```

---

## 🐛 Troubleshooting

### Issue: "No MCP servers found"

**Cause:** Servers not starting or not found

**Solution:**
```bash
# 1. Check if server files exist
ls -la mcp/servers/*.py

# 2. Check Python permissions
chmod +x mcp/servers/*.py

# 3. Start backend and watch logs
DEBUG=True python main.py

# Look for: "MCP servers initialized"
```

---

### Issue: "Tool timeout"

**Cause:** Server not responding within timeout

**Solution:**
```bash
# Check server is running
ps aux | grep ppt_server

# Test server manually
python mcp/servers/1.ppt_server.py

# Check for errors in console output
```

---

### Issue: "SearchTopic returned empty"

**Cause:** DuckDuckGo API failure or network issue

**Solution:**
```bash
# Test search manually
curl "https://duckduckgo.com/?q=machine%20learning&format=json"

# Check internet connection
ping google.com

# Check for rate limiting (wait a few minutes)
```

---

### Issue: "File permission denied"

**Cause:** MCP server can't write to output directory

**Solution:**
```bash
# Check directory permissions
ls -la output/

# Create if missing
mkdir -p output

# Fix permissions
chmod 755 output/

# Run as same user as backend
```

---

## 📊 Performance Metrics

### Expected Latencies

| Tool | Avg Time | Max Time | Notes |
|------|----------|----------|-------|
| create_presentation | 150ms | 500ms | In-memory |
| add_slide | 200ms | 600ms | Per slide |
| write_text_to_slide | 300ms | 1000ms | Depends on bullet count |
| add_image_placeholder | 100ms | 300ms | Metadata only |
| search_topic | 1-3s | 10s | Network dependent |
| fetch_page_summary | 2-4s | 8s | Parsing required |
| apply_theme | 400ms | 1000ms | All slides |
| save_presentation | 500ms | 2000ms | File I/O + PPTX write |

### Concurrency Model

```
Series (Sequential):
  Slide 1 → Slide 2 → Slide 3 → Slide 4 → Slide 5

Parallel (PPT builds while search happens):
  Web Search 1 ─┐
                ├─ PPT adds slide 1
  Web Search 2 ─┤
                ├─ PPT adds slide 2
  Web Search 3 ─┘

Result: ~30% faster than pure sequential
```

---

## 📞 Support

### Debug Mode

```bash
# Enable debug logging
DEBUG=True python ../agent/main.py

# You'll see:
# [DEBUG] Starting MCP server: 1.ppt_server.py
# [DEBUG] Server 1 (PPT) ready
# [DEBUG] Tool call: create_presentation
# [DEBUG] Tool response: {...}
```

### Check Server Status

```bash
# Is server responding?
ps aux | grep python

# Check logs
tail -f mcp_server.log

# Test tool directly
echo '{"method":"tools/list"}' | python 1.ppt_server.py
```

---

## 📚 References

### File Structure
```
mcp/
├── README.md              # This file
├── servers/
│   ├── 1.ppt_server.py              # 6 tools
│   ├── 2.web_search_server.py       # 2 tools
│   ├── 3.filesystem_server.py       # 4 tools
│   ├── 4.theme_server.py            # 4 tools
│   ├── requirements.txt
│   ├── __init__.py
│   └── venv/             # Virtual env
```

### Related Documentation
- [Agent README](../agent/README.md) - MCP client & integration
- [Root README](../README.md) - System overview

---

**The MCP Servers power SlideForage's distributed intelligence!** 🚀

For integration details, see [Agent README](../agent/README.md)
