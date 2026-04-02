# MCP Servers Configuration - Auto-PPT Agent

## Server Architecture

This directory contains 4 specialized MCP servers for autonomous PowerPoint creation:

### 1. PPT Server (1.ppt_server.py)
Purpose: Core PowerPoint manipulation using python-pptx
Tools:
- create_presentation - Initialize new .pptx
- add_slide - Add slides with layouts
- write_text_to_slide - Add title + bullet content
- add_image_placeholder - Add image placeholders
- save_presentation - Save to disk
- get_presentation_info - Query presentation metadata

### 2. Web Search Server (2.web_search_server.py)
Purpose: Fetch real-time content for slides using DuckDuckGo
Tools:
- search_topic - Search for content on a topic
- fetch_page_summary - Extract summary from URL

Rationale: Enables agent to augment content with web data.

### 3. Filesystem Server (3.filesystem_server.py)
Purpose: Clean disk I/O separation
Tools:
- save_file - Save content to disk
- list_output_files - List generated files
- get_file_path - Resolve file paths
- delete_file - Remove files

Rationale: Keeps PPT server pure. Shows MCP maturity.

### 4. Theme Server (4.theme_server.py)
Purpose: Styling and presentation aesthetics
Tools:
- apply_theme - Select from: default, ocean, forest, sunset, midnight
- set_color_scheme - Custom RGB/hex colors
- set_font_style - Font selection and sizing
- get_available_themes - Query all options

Rationale: Makes presentations polished. Differentiator - few agents implement this.

## Installation

pip install -r requirements.txt

## Running Servers

Each server runs as a stdio MCP server:

python3 1.ppt_server.py
python3 2.web_search_server.py
python3 3.filesystem_server.py
python3 4.theme_server.py

## Communication Flow

Agent (LLM Loop)
    down arrow
[Plans: Create 5 slides on topic X]
    down arrow
PPT Server: create_presentation()
    down arrow
Web Search Server: search_topic()
    down arrow
PPT Server: add_slide(), write_text_to_slide()
    down arrow
Theme Server: apply_theme()
    down arrow
PPT Server: save_presentation()
    down arrow
[DONE: .pptx ready]
