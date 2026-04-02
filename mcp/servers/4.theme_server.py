#!/usr/bin/env python3
import json
import mcp.server.stdio
from pptx.util import Pt, RGBColor
from pptx.enum.text import PP_ALIGN

# Available themes and color schemes
AVAILABLE_THEMES = {
    "default": {"name": "Default", "colors": {"primary": (59, 89, 152), "secondary": (243, 109, 67), "text": (0, 0, 0)}},
    "ocean": {"name": "Ocean Blue", "colors": {"primary": (0, 119, 182), "secondary": (140, 199, 237), "text": (255, 255, 255)}},
    "forest": {"name": "Forest Green", "colors": {"primary": (34, 139, 34), "secondary": (144, 238, 144), "text": (255, 255, 255)}},
    "sunset": {"name": "Sunset Orange", "colors": {"primary": (255, 140, 0), "secondary": (255, 165, 0), "text": (255, 255, 255)}},
    "midnight": {"name": "Midnight", "colors": {"primary": (25, 25, 112), "secondary": (70, 130, 180), "text": (255, 255, 255)}}
}

FONT_STYLES = {
    "default": {"name": "Arial", "size": 18},
    "modern": {"name": "Calibri", "size": 16},
    "classic": {"name": "Times New Roman", "size": 20},
    "tech": {"name": "Courier New", "size": 14}
}

# Global theme state
_current_theme = "default"
_current_colors = AVAILABLE_THEMES["default"]["colors"]
_current_font = "default"

async def apply_theme(theme_name: str) -> dict:
    global _current_theme, _current_colors
    
    if theme_name not in AVAILABLE_THEMES:
        return {
            "status": "error",
            "message": f"Theme '{theme_name}' not found. Available: {list(AVAILABLE_THEMES.keys())}"
        }
    
    _current_theme = theme_name
    _current_colors = AVAILABLE_THEMES[theme_name]["colors"]
    
    return {
        "status": "success",
        "theme_applied": theme_name,
        "theme_info": AVAILABLE_THEMES[theme_name],
        "message": f"Theme '{theme_name}' applied successfully"
    }

async def set_color_scheme(primary: str, secondary: str, text: str) -> dict:
    global _current_colors
    
    try:
        def parse_color(color_str):
            if color_str.startswith("#"):
                hex_str = color_str.lstrip("#")
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            elif "," in color_str:
                return tuple(int(x.strip()) for x in color_str.split(","))
            else:
                return (0, 0, 0)
        
        _current_colors = {
            "primary": parse_color(primary),
            "secondary": parse_color(secondary),
            "text": parse_color(text)
        }
        
        return {
            "status": "success",
            "colors": _current_colors,
            "message": "Color scheme applied successfully"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def set_font_style(font_name: str, font_size: int = 18) -> dict:
    global _current_font
    
    if font_name not in FONT_STYLES:
        return {
            "status": "error",
            "message": f"Font style '{font_name}' not found. Available: {list(FONT_STYLES.keys())}"
        }
    
    _current_font = font_name
    
    return {
        "status": "success",
        "font": font_name,
        "size": font_size,
        "font_config": FONT_STYLES[font_name],
        "message": "Font style applied successfully"
    }

async def get_available_themes() -> dict:
    return {
        "status": "success",
        "themes": list(AVAILABLE_THEMES.keys()),
        "theme_details": AVAILABLE_THEMES,
        "font_styles": FONT_STYLES,
        "current_theme": _current_theme,
        "current_colors": _current_colors,
        "current_font": _current_font
    }

async def call_tool(name: str, arguments: dict):
    if name == "apply_theme":
        return await apply_theme(arguments["theme_name"])
    elif name == "set_color_scheme":
        return await set_color_scheme(arguments["primary"], arguments["secondary"], arguments["text"])
    elif name == "set_font_style":
        return await set_font_style(arguments["font_name"], arguments.get("font_size", 18))
    elif name == "get_available_themes":
        return await get_available_themes()
    else:
        return {"status": "error", "message": f"Unknown tool: {name}"}

async def main():
    import sys
    import json
    while True:
        line = sys.stdin.readline()
        if not line: break
        try:
            req = json.loads(line)
            if req.get("method") == "tools/call":
                name = req["params"]["name"]
                args = req["params"].get("arguments", {})
                result = await call_tool(name, args)
                print(json.dumps(result))
                sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
