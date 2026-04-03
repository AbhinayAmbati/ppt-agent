#!/usr/bin/env python3
"""
PPT MCP Server - Beautiful Styled Version
- Widescreen 16:9 slides (not square)
- Full background color per slide
- Styled title with accent bar
- Bullet points with proper fonts and spacing
- Alternating accent colors per slide
"""

import sys
import json
import asyncio
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import copy

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

_current_presentation = None

# ── THEME DEFINITIONS ──────────────────────────────────────────────────────────
THEMES = {
    "ocean": {
        "bg":          RGBColor(0x0A, 0x29, 0x4A),   # deep navy
        "title_slide_bg": RGBColor(0x05, 0x14, 0x2E),
        "accent":      RGBColor(0x00, 0xB4, 0xD8),   # cyan
        "accent2":     RGBColor(0x90, 0xE0, 0xEF),   # light blue
        "title_fg":    RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg": RGBColor(0x90, 0xE0, 0xEF),
        "bullet_fg":   RGBColor(0xE0, 0xF7, 0xFF),
        "bar":         RGBColor(0x00, 0xB4, 0xD8),
        "title_font":  "Calibri",
        "body_font":   "Calibri",
    },
    "corporate": {
        "bg":          RGBColor(0x1A, 0x1A, 0x2E),
        "title_slide_bg": RGBColor(0x10, 0x10, 0x20),
        "accent":      RGBColor(0xE9, 0x4F, 0x37),
        "accent2":     RGBColor(0xF5, 0xA6, 0x23),
        "title_fg":    RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg": RGBColor(0xF5, 0xA6, 0x23),
        "bullet_fg":   RGBColor(0xF0, 0xF0, 0xF0),
        "bar":         RGBColor(0xE9, 0x4F, 0x37),
        "title_font":  "Calibri",
        "body_font":   "Calibri",
    },
    "minimal": {
        "bg":          RGBColor(0xF8, 0xF9, 0xFA),
        "title_slide_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "accent":      RGBColor(0x21, 0x96, 0xF3),
        "accent2":     RGBColor(0x64, 0xB5, 0xF6),
        "title_fg":    RGBColor(0x1A, 0x1A, 0x2E),
        "subtitle_fg": RGBColor(0x21, 0x96, 0xF3),
        "bullet_fg":   RGBColor(0x2C, 0x2C, 0x3E),
        "bar":         RGBColor(0x21, 0x96, 0xF3),
        "title_font":  "Calibri",
        "body_font":   "Calibri",
    },
    "dark": {
        "bg":          RGBColor(0x12, 0x12, 0x12),
        "title_slide_bg": RGBColor(0x08, 0x08, 0x08),
        "accent":      RGBColor(0xBB, 0x86, 0xFC),
        "accent2":     RGBColor(0x03, 0xDA, 0xC6),
        "title_fg":    RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg": RGBColor(0xBB, 0x86, 0xFC),
        "bullet_fg":   RGBColor(0xE0, 0xE0, 0xE0),
        "bar":         RGBColor(0xBB, 0x86, 0xFC),
        "title_font":  "Calibri",
        "body_font":   "Calibri",
    },
    "academic": {
        "bg":          RGBColor(0x1B, 0x2A, 0x4A),
        "title_slide_bg": RGBColor(0x0D, 0x1B, 0x33),
        "accent":      RGBColor(0xC8, 0xA2, 0x00),
        "accent2":     RGBColor(0xE8, 0xD0, 0x70),
        "title_fg":    RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg": RGBColor(0xC8, 0xA2, 0x00),
        "bullet_fg":   RGBColor(0xF0, 0xEC, 0xD8),
        "bar":         RGBColor(0xC8, 0xA2, 0x00),
        "title_font":  "Georgia",
        "body_font":   "Calibri",
    },
}

DEFAULT_THEME = "ocean"
_active_theme = THEMES[DEFAULT_THEME]


# ── HELPERS ─────────────────────────────────────────────────────────────────────

def _set_bg(slide, color: RGBColor):
    """Fill slide background with a solid color."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_rect(slide, x, y, w, h, color: RGBColor):
    """Add a filled rectangle shape."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()  # no border
    return shape


def _set_text_style(run, color: RGBColor, size_pt: int, bold: bool = False, font_name: str = "Calibri"):
    run.font.color.rgb = color
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.name = font_name


def _style_title_slide(slide, title: str, subtitle: str, theme: dict):
    """Style the opening title slide."""
    _set_bg(slide, theme["title_slide_bg"])

    # Left accent bar
    _add_rect(slide, 0, 0, 0.12, 7.5, theme["accent"])

    # Bottom accent strip
    _add_rect(slide, 0, 6.8, 13.33, 0.7, theme["accent"])

    # Title text box
    from pptx.util import Inches, Pt
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(12.0), Inches(2.0))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = title
    _set_text_style(run, theme["title_fg"], 44, bold=True, font_name=theme["title_font"])

    # Subtitle text box
    txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(3.9), Inches(12.0), Inches(1.2))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.LEFT
    run2 = p2.add_run()
    run2.text = subtitle
    _set_text_style(run2, theme["subtitle_fg"], 22, bold=False, font_name=theme["body_font"])

    # Remove default placeholders (they look ugly blank)
    sp_tree = slide.shapes._spTree
    for ph in slide.placeholders:
        sp = ph._element
        sp_tree.remove(sp)


def _style_content_slide(slide, title: str, bullets: list, theme: dict, slide_num: int):
    """Style a content slide with background, title bar, and bullets."""
    _set_bg(slide, theme["bg"])

    # Top title bar
    _add_rect(slide, 0, 0, 13.33, 1.4, theme["accent"])

    # Bottom accent strip
    accent_color = theme["accent2"] if slide_num % 2 == 0 else theme["accent"]
    _add_rect(slide, 0, 7.1, 13.33, 0.4, accent_color)

    # Slide number dot
    dot = slide.shapes.add_shape(1, Inches(12.6), Inches(0.3), Inches(0.5), Inches(0.5))
    dot.fill.solid()
    dot.fill.fore_color.rgb = theme["bg"]
    dot.line.fill.background()
    dot_tf = dot.text_frame
    dot_p = dot_tf.paragraphs[0]
    dot_p.alignment = PP_ALIGN.CENTER
    dot_run = dot_p.add_run()
    dot_run.text = str(slide_num)
    dot_run.font.color.rgb = theme["accent"]
    dot_run.font.size = Pt(12)
    dot_run.font.bold = True
    dot_run.font.name = theme["title_font"]

    # Title text on bar
    title_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(12.5), Inches(1.1))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.alignment = PP_ALIGN.LEFT
    run_title = p_title.add_run()
    run_title.text = title
    _set_text_style(run_title, theme["title_fg"], 32, bold=True, font_name=theme["title_font"])

    # Bullets area
    bullet_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.6), Inches(12.3), Inches(5.2))
    tf_bullets = bullet_box.text_frame
    tf_bullets.word_wrap = True

    for i, bullet_text in enumerate(bullets):
        p = tf_bullets.paragraphs[0] if i == 0 else tf_bullets.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(6)

        # Bullet dot run
        dot_run = p.add_run()
        dot_run.text = "● "
        dot_run.font.color.rgb = theme["accent"] if i % 2 == 0 else theme["accent2"]
        dot_run.font.size = Pt(18)
        dot_run.font.name = theme["body_font"]

        # Text run
        text_run = p.add_run()
        text_run.text = str(bullet_text)
        _set_text_style(text_run, theme["bullet_fg"], 18, bold=False, font_name=theme["body_font"])

    # Remove default placeholders
    sp_tree = slide.shapes._spTree
    for ph in slide.placeholders:
        sp_tree.remove(ph._element)


# ── TOOL FUNCTIONS ──────────────────────────────────────────────────────────────

async def create_presentation(title: str, subtitle: str = "", theme_name: str = DEFAULT_THEME) -> dict:
    global _current_presentation, _active_theme
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    _active_theme = theme

    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    # Use blank layout for full control
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    _style_title_slide(slide, title, subtitle, theme)

    _current_presentation = prs
    return {"status": "success", "message": "Presentation created", "slide_count": 1}


async def add_slide(layout_type: str = "title_and_content") -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    blank_layout = _current_presentation.slide_layouts[6]
    _current_presentation.slides.add_slide(blank_layout)
    return {"status": "success", "message": "Slide added", "slide_count": len(_current_presentation.slides)}


async def write_text_to_slide(slide_index: int, title: str, content: list) -> dict:
    global _current_presentation, _active_theme
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    slides = _current_presentation.slides
    if slide_index < 0 or slide_index >= len(slides):
        return {"status": "error", "message": f"slide_index {slide_index} out of range (total={len(slides)})"}
    slide = slides[slide_index]
    _style_content_slide(slide, title, content, _active_theme, slide_num=slide_index)
    return {"status": "success", "message": "Text written", "bullet_count": len(content)}


async def set_theme(theme_name: str) -> dict:
    global _active_theme
    if theme_name not in THEMES:
        return {"status": "error", "message": f"Unknown theme. Available: {list(THEMES.keys())}"}
    _active_theme = THEMES[theme_name]
    return {"status": "success", "theme": theme_name}


async def save_presentation(file_path: str) -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(file_path).name
    full_path = OUTPUTS_DIR / filename
    _current_presentation.save(str(full_path))
    return {"status": "success", "message": "Saved", "file_path": str(full_path)}


async def get_presentation_info() -> dict:
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    return {"status": "success", "slide_count": len(_current_presentation.slides)}


async def add_image_placeholder(slide_index: int, placeholder_text: str = "[Image]") -> dict:
    global _current_presentation, _active_theme
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    slides = _current_presentation.slides
    if slide_index < 0 or slide_index >= len(slides):
        return {"status": "error", "message": f"slide_index {slide_index} out of range"}
    slide = slides[slide_index]
    box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(2.5))
    box.fill.solid()
    box.fill.fore_color.rgb = _active_theme["accent"]
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = placeholder_text
    run.font.color.rgb = _active_theme["title_fg"]
    run.font.size = Pt(20)
    run.font.bold = True
    return {"status": "success", "message": "Image placeholder added"}


async def call_tool(name: str, arguments: dict) -> dict:
    try:
        if name == "create_presentation":
            return await create_presentation(
                arguments["title"],
                arguments.get("subtitle", ""),
                arguments.get("theme_name", DEFAULT_THEME),
            )
        elif name == "add_slide":
            return await add_slide(arguments.get("layout_type", "title_and_content"))
        elif name == "write_text_to_slide":
            return await write_text_to_slide(
                arguments["slide_index"], arguments["title"], arguments["content"]
            )
        elif name == "save_presentation":
            return await save_presentation(arguments["file_path"])
        elif name == "get_presentation_info":
            return await get_presentation_info()
        elif name == "add_image_placeholder":
            return await add_image_placeholder(
                arguments["slide_index"], arguments.get("placeholder_text", "[Image]")
            )
        elif name == "set_theme":
            return await set_theme(arguments["theme_name"])
        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}


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
