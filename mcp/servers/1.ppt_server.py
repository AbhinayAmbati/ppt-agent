#!/usr/bin/env python3
"""
PPT MCP Server - v3.2
Fixes:
- Uniform bullet symbol (▸) and color across all bullet points — no more mixed shapes
- write_text_to_slide: content items coerced to str defensively
- call_tool: returns full traceback in error response for easier debugging
- Text vertically centered in bullet area (not top-aligned)
- Beautiful image placeholder box with icon + caption
- Two-column layout support (bullets left, image right)
- Conclusion slide gets special "thank you" styling
- All text uses auto_size=False to prevent overflow
"""

import sys
import json
import asyncio
import traceback as _tb
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUTS_DIR  = PROJECT_ROOT / "outputs"

_current_presentation = None

# Single bullet symbol used everywhere — change this one constant to restyle all slides
BULLET_SYMBOL = "▸"

# ── THEMES ────────────────────────────────────────────────────────────────────
THEMES = {
    "ocean": {
        "bg":             RGBColor(0x0A, 0x29, 0x4A),
        "title_slide_bg": RGBColor(0x05, 0x14, 0x2E),
        "accent":         RGBColor(0x00, 0xB4, 0xD8),
        "accent2":        RGBColor(0x90, 0xE0, 0xEF),
        "title_fg":       RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg":    RGBColor(0x90, 0xE0, 0xEF),
        "bullet_fg":      RGBColor(0xE0, 0xF7, 0xFF),
        "img_bg":         RGBColor(0x05, 0x3A, 0x5E),
        "title_font":     "Calibri",
        "body_font":      "Calibri",
    },
    "corporate": {
        "bg":             RGBColor(0x1A, 0x1A, 0x2E),
        "title_slide_bg": RGBColor(0x10, 0x10, 0x20),
        "accent":         RGBColor(0xE9, 0x4F, 0x37),
        "accent2":        RGBColor(0xF5, 0xA6, 0x23),
        "title_fg":       RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg":    RGBColor(0xF5, 0xA6, 0x23),
        "bullet_fg":      RGBColor(0xF0, 0xF0, 0xF0),
        "img_bg":         RGBColor(0x2E, 0x1A, 0x1A),
        "title_font":     "Calibri",
        "body_font":      "Calibri",
    },
    "minimal": {
        "bg":             RGBColor(0xF8, 0xF9, 0xFA),
        "title_slide_bg": RGBColor(0xFF, 0xFF, 0xFF),
        "accent":         RGBColor(0x21, 0x96, 0xF3),
        "accent2":        RGBColor(0x64, 0xB5, 0xF6),
        "title_fg":       RGBColor(0x1A, 0x1A, 0x2E),
        "subtitle_fg":    RGBColor(0x21, 0x96, 0xF3),
        "bullet_fg":      RGBColor(0x2C, 0x2C, 0x3E),
        "img_bg":         RGBColor(0xDD, 0xEE, 0xFF),
        "title_font":     "Calibri",
        "body_font":      "Calibri",
    },
    "dark": {
        "bg":             RGBColor(0x12, 0x12, 0x12),
        "title_slide_bg": RGBColor(0x08, 0x08, 0x08),
        "accent":         RGBColor(0xBB, 0x86, 0xFC),
        "accent2":        RGBColor(0x03, 0xDA, 0xC6),
        "title_fg":       RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg":    RGBColor(0xBB, 0x86, 0xFC),
        "bullet_fg":      RGBColor(0xE0, 0xE0, 0xE0),
        "img_bg":         RGBColor(0x1E, 0x1E, 0x2E),
        "title_font":     "Calibri",
        "body_font":      "Calibri",
    },
    "academic": {
        "bg":             RGBColor(0x1B, 0x2A, 0x4A),
        "title_slide_bg": RGBColor(0x0D, 0x1B, 0x33),
        "accent":         RGBColor(0xC8, 0xA2, 0x00),
        "accent2":        RGBColor(0xE8, 0xD0, 0x70),
        "title_fg":       RGBColor(0xFF, 0xFF, 0xFF),
        "subtitle_fg":    RGBColor(0xC8, 0xA2, 0x00),
        "bullet_fg":      RGBColor(0xF0, 0xEC, 0xD8),
        "img_bg":         RGBColor(0x0D, 0x1B, 0x33),
        "title_font":     "Georgia",
        "body_font":      "Calibri",
    },
}

DEFAULT_THEME = "ocean"
_active_theme = THEMES[DEFAULT_THEME]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _set_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_rect(slide, x, y, w, h, color: RGBColor, border_color=None):
    from pptx.util import Pt as _Pt
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = _Pt(1)
    else:
        shape.line.fill.background()
    return shape


def _styled_run(para, text, color, size_pt, bold=False, font="Calibri"):
    run = para.add_run()
    run.text = str(text)
    run.font.color.rgb = color
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.name = font
    return run


def _remove_placeholders(slide):
    sp_tree = slide.shapes._spTree
    for ph in list(slide.placeholders):
        sp_tree.remove(ph._element)


# ── TITLE SLIDE ───────────────────────────────────────────────────────────────

def _style_title_slide(slide, title: str, subtitle: str, theme: dict):
    _set_bg(slide, theme["title_slide_bg"])
    _remove_placeholders(slide)

    _add_rect(slide, 0, 0, 0.15, 7.5, theme["accent"])
    _add_rect(slide, 0, 6.7, 13.33, 0.8, theme["accent"])
    _add_rect(slide, 12.53, 0, 0.8, 0.8, theme["accent2"])

    tb = slide.shapes.add_textbox(Inches(0.5), Inches(1.6), Inches(12.0), Inches(2.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    _styled_run(p, title, theme["title_fg"], 46, bold=True, font=theme["title_font"])

    _add_rect(slide, 0.5, 4.3, 5.0, 0.05, theme["accent"])

    tb2 = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(11.5), Inches(1.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.LEFT
    _styled_run(p2, subtitle, theme["subtitle_fg"], 22, bold=False, font=theme["body_font"])

    tb3 = slide.shapes.add_textbox(Inches(0.4), Inches(6.75), Inches(8.0), Inches(0.6))
    tf3 = tb3.text_frame
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.LEFT
    _styled_run(p3, "AUTO-GENERATED PRESENTATION", theme["title_fg"], 10, bold=True, font=theme["body_font"])


# ── CONTENT SLIDE ─────────────────────────────────────────────────────────────

def _style_content_slide(slide, title: str, bullets: list, theme: dict,
                          slide_num: int, include_image: bool = False):
    _set_bg(slide, theme["bg"])
    _remove_placeholders(slide)

    _add_rect(slide, 0, 0, 13.33, 1.45, theme["accent"])

    strip_color = theme["accent2"] if slide_num % 2 == 0 else theme["accent"]
    _add_rect(slide, 0, 7.15, 13.33, 0.35, strip_color)

    pill = _add_rect(slide, 12.55, 0.45, 0.55, 0.45, theme["bg"])
    pill_tf = pill.text_frame
    pill_p = pill_tf.paragraphs[0]
    pill_p.alignment = PP_ALIGN.CENTER
    _styled_run(pill_p, str(slide_num), theme["accent2"], 11, bold=True, font=theme["title_font"])

    title_tb = slide.shapes.add_textbox(Inches(0.35), Inches(0.08), Inches(12.0), Inches(1.28))
    title_tf = title_tb.text_frame
    title_tf.word_wrap = True
    title_tf.auto_size = None
    title_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_title = title_tf.paragraphs[0]
    p_title.alignment = PP_ALIGN.LEFT
    _styled_run(p_title, title, theme["title_fg"], 30, bold=True, font=theme["title_font"])

    if include_image:
        _style_bullets_box(slide, bullets, theme, x=0.3, y=1.55, w=7.5, h=5.4)
        _style_image_placeholder(slide, theme, x=8.05, y=1.55, w=4.9, h=5.4,
                                  caption=f"[{title} Image]")
    else:
        _style_bullets_box(slide, bullets, theme, x=0.4, y=1.55, w=12.5, h=5.4)


def _style_bullets_box(slide, bullets, theme, x, y, w, h):
    """
    Bullet point text box.
    All bullets use the same symbol (BULLET_SYMBOL) and the same accent color
    so the slide looks visually consistent.
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    from pptx.util import Pt as _Pt

    for i, text in enumerate(bullets):
        text = str(text).strip() if text is not None else ""
        if not text:
            continue

        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = _Pt(10)
        p.space_after  = _Pt(4)

        # ── UNIFORM bullet: same symbol, same color for every point ──
        _styled_run(p, f"{BULLET_SYMBOL}  ", theme["accent"], 16, bold=True,
                    font=theme["body_font"])
        _styled_run(p, text, theme["bullet_fg"], 18, bold=False,
                    font=theme["body_font"])


def _style_image_placeholder(slide, theme, x, y, w, h, caption="[Image]"):
    _add_rect(slide, x, y, w, h, theme["img_bg"], border_color=theme["accent2"])

    icon_tb = slide.shapes.add_textbox(
        Inches(x + w/2 - 0.7), Inches(y + h/2 - 0.85), Inches(1.4), Inches(0.9)
    )
    icon_tf = icon_tb.text_frame
    icon_p = icon_tf.paragraphs[0]
    icon_p.alignment = PP_ALIGN.CENTER
    _styled_run(icon_p, "🖼", theme["accent2"], 36, font="Segoe UI Emoji")

    cap_tb = slide.shapes.add_textbox(
        Inches(x + 0.2), Inches(y + h/2 + 0.1), Inches(w - 0.4), Inches(0.8)
    )
    cap_tf = cap_tb.text_frame
    cap_tf.word_wrap = True
    cap_p = cap_tf.paragraphs[0]
    cap_p.alignment = PP_ALIGN.CENTER
    _styled_run(cap_p, caption, theme["accent2"], 13, bold=False, font=theme["body_font"])

    hint_tb = slide.shapes.add_textbox(
        Inches(x + 0.2), Inches(y + h - 0.55), Inches(w - 0.4), Inches(0.45)
    )
    hint_tf = hint_tb.text_frame
    hint_p = hint_tf.paragraphs[0]
    hint_p.alignment = PP_ALIGN.CENTER
    _styled_run(hint_p, "[ Replace with actual image ]",
                theme["bullet_fg"], 9, bold=False, font=theme["body_font"])


# ── CONCLUSION SLIDE ──────────────────────────────────────────────────────────

def _style_conclusion_slide(slide, title: str, bullets: list, theme: dict, slide_num: int):
    _set_bg(slide, theme["title_slide_bg"])
    _remove_placeholders(slide)

    _add_rect(slide, 0, 0, 13.33, 0.15, theme["accent"])
    _add_rect(slide, 0, 7.35, 13.33, 0.15, theme["accent"])

    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(1.5))
    tf = tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _styled_run(p, title, theme["accent"], 36, bold=True, font=theme["title_font"])

    _add_rect(slide, 2.0, 1.9, 9.33, 0.06, theme["accent2"])

    _style_bullets_box(slide, bullets, theme, x=1.5, y=2.1, w=10.33, h=4.2)

    pill = _add_rect(slide, 12.55, 0.2, 0.55, 0.45, theme["accent"])
    pill_tf = pill.text_frame
    pill_p = pill_tf.paragraphs[0]
    pill_p.alignment = PP_ALIGN.CENTER
    _styled_run(pill_p, str(slide_num), theme["title_fg"], 11, bold=True, font=theme["title_font"])


# ── TOOL FUNCTIONS ────────────────────────────────────────────────────────────

async def create_presentation(title: str, subtitle: str = "",
                               theme_name: str = DEFAULT_THEME) -> dict:
    global _current_presentation, _active_theme
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    _active_theme = theme

    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    _style_title_slide(slide, title, subtitle, theme)

    _current_presentation = prs
    return {"status": "success", "message": "Presentation created", "slide_count": 1}


async def add_slide(layout_type: str = "title_and_content") -> dict:
    global _current_presentation
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    blank = _current_presentation.slide_layouts[6]
    _current_presentation.slides.add_slide(blank)
    return {"status": "success", "message": "Slide added",
            "slide_count": len(_current_presentation.slides)}


async def write_text_to_slide(slide_index: int, title: str, content: list,
                               include_image: bool = False,
                               is_conclusion: bool = False) -> dict:
    global _current_presentation, _active_theme
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}

    slides = _current_presentation.slides
    if slide_index < 0 or slide_index >= len(slides):
        return {
            "status": "error",
            "message": (
                f"slide_index {slide_index} out of range "
                f"(total slides={len(slides)}). "
                f"Valid range: 0 – {len(slides)-1}."
            )
        }

    clean_content = [str(item).strip() for item in (content or []) if item is not None]
    if not clean_content:
        clean_content = [f"Key information about {title}"]

    slide = slides[slide_index]
    try:
        if is_conclusion:
            _style_conclusion_slide(slide, str(title), clean_content, _active_theme,
                                    slide_num=slide_index)
        else:
            _style_content_slide(slide, str(title), clean_content, _active_theme,
                                  slide_num=slide_index, include_image=bool(include_image))
    except Exception as exc:
        return {
            "status":  "error",
            "message": f"Styling failed: {exc}",
            "trace":   _tb.format_exc(),
        }

    return {"status": "success", "message": "Text written", "bullet_count": len(clean_content)}


async def add_image_placeholder(slide_index: int, placeholder_text: str = "[Image]") -> dict:
    global _current_presentation, _active_theme
    if _current_presentation is None:
        return {"status": "error", "message": "No active presentation"}
    slides = _current_presentation.slides
    if slide_index < 0 or slide_index >= len(slides):
        return {"status": "error", "message": f"slide_index {slide_index} out of range"}
    slide = slides[slide_index]
    _style_image_placeholder(slide, _active_theme, x=1.5, y=2.0, w=10.33, h=4.0,
                              caption=placeholder_text)
    return {"status": "success", "message": "Image placeholder added"}


async def set_theme(theme_name: str) -> dict:
    global _active_theme
    if theme_name not in THEMES:
        return {"status": "error",
                "message": f"Unknown theme. Available: {list(THEMES.keys())}"}
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
                arguments["slide_index"],
                arguments["title"],
                arguments["content"],
                include_image=arguments.get("include_image", False),
                is_conclusion=arguments.get("is_conclusion", False),
            )
        elif name == "add_image_placeholder":
            return await add_image_placeholder(
                arguments["slide_index"],
                arguments.get("placeholder_text", "[Image]"),
            )
        elif name == "save_presentation":
            return await save_presentation(arguments["file_path"])
        elif name == "get_presentation_info":
            return await get_presentation_info()
        elif name == "set_theme":
            return await set_theme(arguments["theme_name"])
        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}
    except Exception as e:
        return {"status": "error", "message": str(e), "trace": _tb.format_exc()}


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
                result = await call_tool(req["params"]["name"],
                                         req["params"].get("arguments", {}))
            else:
                result = {"status": "error", "message": f"Unknown method: {req.get('method')}"}
        except Exception as e:
            result = {"status": "error", "message": f"Parse error: {e}"}
        stdout.write((json.dumps(result) + "\n").encode("utf-8"))
        stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
