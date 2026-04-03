#!/usr/bin/env python3
"""
PPT MCP Server - FIXED VERSION
Issues fixed:
1. Uses binary stdin/stdout to match the fixed mcp_client (no text=True)
2. slide_count returned correctly so agent can track actual indices
3. outputs/ folder resolved relative to project root, not cwd
"""

import sys
import json
import asyncio
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

# Resolve outputs/ relative to THIS file's location (mcp/servers/ -> project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

_current_presentation = None


async def create_presentation(title: str, subtitle: str = "") -> dict:
    global _current_presentation
    _current_presentation = Presentation()
    slide = _current_presentation.slides.add_slide(_current_presentation.slide_layouts[0])
    slide.shapes.title.text = title
    if len(slide.placeholders) > 1:
        slide.placeholders[1].text = subtitle
    return {
        "status": "success",
        "message": "Presentation created",
        "slide_count": len(_current_presentation.slides),
    }


async def add_slide(layout_type: str = "title_and_content") -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    layout_mapping = {
        "title_only": 5,
        "blank": 6,
        "title_and_content": 1,
        "section_header": 2,
    }
    layout_index = layout_mapping.get(layout_type, 1)
    _current_presentation.slides.add_slide(_current_presentation.slide_layouts[layout_index])
    return {
        "status": "success",
        "message": "Slide added",
        "slide_count": len(_current_presentation.slides),
    }


async def write_text_to_slide(slide_index: int, title: str, content: list) -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    slides = _current_presentation.slides
    if slide_index < 0 or slide_index >= len(slides):
        return {"status": "error", "message": f"slide_index {slide_index} out of range (total={len(slides)})"}
    slide = slides[slide_index]
    if slide.shapes.title:
        slide.shapes.title.text = str(title)
    if len(slide.placeholders) > 1:
        tf = slide.placeholders[1].text_frame
        tf.clear()
        for i, txt in enumerate(content):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = str(txt)
    return {"status": "success", "message": "Text written", "bullet_count": len(content)}


async def add_image_placeholder(slide_index: int, placeholder_text: str = "[Image]") -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    slides = _current_presentation.slides
    if slide_index < 0 or slide_index >= len(slides):
        return {"status": "error", "message": f"slide_index {slide_index} out of range"}
    slide = slides[slide_index]
    tb = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(3))
    tb.text_frame.paragraphs[0].text = placeholder_text
    return {"status": "success", "message": "Placeholder added"}


async def save_presentation(file_path: str) -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    # Always save under project outputs/ regardless of what path is passed
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(file_path).name
    full_path = OUTPUTS_DIR / filename
    _current_presentation.save(str(full_path))
    return {"status": "success", "message": "Saved", "file_path": str(full_path)}


async def get_presentation_info() -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    return {"status": "success", "slide_count": len(_current_presentation.slides)}


async def call_tool(name: str, arguments: dict) -> dict:
    try:
        if name == "create_presentation":
            return await create_presentation(arguments["title"], arguments.get("subtitle", ""))
        elif name == "add_slide":
            return await add_slide(arguments.get("layout_type", "title_and_content"))
        elif name == "write_text_to_slide":
            return await write_text_to_slide(
                arguments["slide_index"], arguments["title"], arguments["content"]
            )
        elif name == "add_image_placeholder":
            return await add_image_placeholder(
                arguments["slide_index"], arguments.get("placeholder_text", "[Image]")
            )
        elif name == "save_presentation":
            return await save_presentation(arguments["file_path"])
        elif name == "get_presentation_info":
            return await get_presentation_info()
        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    # KEY FIX: Use binary buffer for stdin/stdout to match mcp_client binary mode
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    while True:
        line = stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line.decode("utf-8").strip())
            if req.get("method") == "tools/call":
                name = req["params"]["name"]
                args = req["params"].get("arguments", {})
                result = await call_tool(name, args)
            else:
                result = {"status": "error", "message": f"Unknown method: {req.get('method')}"}
        except Exception as e:
            result = {"status": "error", "message": f"Parse error: {e}"}

        stdout.write((json.dumps(result) + "\n").encode("utf-8"))
        stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
