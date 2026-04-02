#!/usr/bin/env python3
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
import mcp.server.stdio
from mcp.types import Tool, TextContent

_current_presentation = None
_presentation_path = None

async def create_presentation(title, subtitle=''):
    global _current_presentation, _presentation_path
    _current_presentation = Presentation()
    slide = _current_presentation.slides.add_slide(_current_presentation.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle
    return {'status': 'success', 'message': f'Presentation created', 'slide_count': 1}

async def add_slide(layout_type='title_and_content'):
    global _current_presentation
    if _current_presentation is None:
        return {'status': 'error', 'message': 'No presentation created'}
    layout_mapping = {'title_only': 5, 'blank': 6, 'title_and_content': 1, 'section_header': 2}
    layout_index = layout_mapping.get(layout_type, 1)
    _current_presentation.slides.add_slide(_current_presentation.slide_layouts[layout_index])
    return {'status': 'success', 'message': 'Slide added', 'slide_count': len(_current_presentation.slides)}

async def write_text_to_slide(slide_index, title, content):
    global _current_presentation
    if _current_presentation is None or slide_index >= len(_current_presentation.slides):
        return {'status': 'error', 'message': 'Invalid slide'}
    slide = _current_presentation.slides[slide_index]
    if slide.shapes.title:
        slide.shapes.title.text = title
    if len(slide.placeholders) > 1:
        text_frame = slide.placeholders[1].text_frame
        text_frame.clear()
        for i, txt in enumerate(content):
            p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
            p.text = str(txt)
    return {'status': 'success', 'message': 'Text written', 'bullet_count': len(content)}

async def add_image_placeholder(slide_index, placeholder_text='[Image]'):
    global _current_presentation
    if _current_presentation is None or slide_index >= len(_current_presentation.slides):
        return {'status': 'error', 'message': 'Invalid slide'}
    slide = _current_presentation.slides[slide_index]
    tb = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(3))
    tb.text_frame.paragraphs[0].text = placeholder_text
    return {'status': 'success', 'message': 'Placeholder added'}

async def save_presentation(file_path):
    global _current_presentation, _presentation_path
    if _current_presentation is None:
        return {'status': 'error', 'message': 'No presentation'}
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    _current_presentation.save(file_path)
    _presentation_path = file_path
    return {'status': 'success', 'message': 'Saved', 'file_path': file_path}

async def get_presentation_info():
    global _current_presentation
    if _current_presentation is None:
        return {'status': 'error', 'message': 'No presentation'}
    return {'status': 'success', 'slide_count': len(_current_presentation.slides)}

async def main():
    server = mcp.server.stdio.StdioServer()
    @server.list_tools()
    async def list_tools():
        return [
            Tool(name='create_presentation', description='Create presentation', inputSchema={'type': 'object', 'properties': {'title': {'type': 'string'}, 'subtitle': {'type': 'string'}}, 'required': ['title']}),
            Tool(name='add_slide', description='Add slide', inputSchema={'type': 'object', 'properties': {'layout_type': {'type': 'string'}}}),
            Tool(name='write_text_to_slide', description='Write text', inputSchema={'type': 'object', 'properties': {'slide_index': {'type': 'integer'}, 'title': {'type': 'string'}, 'content': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['slide_index', 'title', 'content']}),
            Tool(name='add_image_placeholder', description='Add image', inputSchema={'type': 'object', 'properties': {'slide_index': {'type': 'integer'}, 'placeholder_text': {'type': 'string'}}, 'required': ['slide_index']}),
            Tool(name='save_presentation', description='Save', inputSchema={'type': 'object', 'properties': {'file_path': {'type': 'string'}}, 'required': ['file_path']}),
            Tool(name='get_presentation_info', description='Get info', inputSchema={'type': 'object', 'properties': {}})
        ]
    @server.call_tool()
    async def call_tool(name, arguments):
        if name == 'create_presentation': result = await create_presentation(arguments['title'], arguments.get('subtitle', ''))
        elif name == 'add_slide': result = await add_slide(arguments.get('layout_type', 'title_and_content'))
        elif name == 'write_text_to_slide': result = await write_text_to_slide(arguments['slide_index'], arguments['title'], arguments['content'])
        elif name == 'add_image_placeholder': result = await add_image_placeholder(arguments['slide_index'], arguments.get('placeholder_text', '[Image]'))
        elif name == 'save_presentation': result = await save_presentation(arguments['file_path'])
        elif name == 'get_presentation_info': result = await get_presentation_info()
        else: result = {'status': 'error', 'message': 'Unknown tool'}
        return [TextContent(type='text', text=json.dumps(result))]
    async with server:
        await server.wait_for_shutdown()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
