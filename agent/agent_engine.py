"""
Agent Engine - Agentic Loop Implementation
PLAN -> EXECUTE -> SAVE architecture
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SlideStructure(BaseModel):
    """Represents a single slide"""
    index: int
    title: str
    bullet_points: List[str]
    include_image: bool = False

class PresentationPlan(BaseModel):
    """Represents the planned presentation"""
    title: str
    subtitle: str
    num_slides: int
    slides: List[SlideStructure]

class AgentEngine:
    """
    Main agent engine implementing the agentic loop
    PHASE 1: PLAN - Use LLM to generate slide structure
    PHASE 2: EXECUTE - Call MCP servers for each slide
    PHASE 3: SAVE - Save to disk
    """
    
    def __init__(self, hf_token: str = None):
        self.hf_token = hf_token
        self.llm = None
        logger.info("Agent Engine initialized")
        
    async def create_presentation(self, user_prompt: str, mcp_client) -> Dict[str, Any]:
        """
        Main orchestrator implementing agentic loop
        """
        logger.info(f"Starting presentation creation: {user_prompt[:50]}...")
        
        try:
            # PHASE 1: PLANNING
            logger.info("PHASE 1: Planning slide structure...")
            plan = self._create_default_plan(user_prompt)
            logger.info(f"Created plan with {plan.num_slides} slides")
            
            # PHASE 2: CREATE PRESENTATION
            logger.info("PHASE 2: Creating presentation...")
            create_result = await mcp_client.call_tool(
                "ppt_server",
                "create_presentation",
                {"title": plan.title, "subtitle": plan.subtitle}
            )
            
            if not create_result or create_result.get("status") != "success":
                return {"status": "error", "message": "Failed to create presentation"}
            
            # PHASE 3: BUILD SLIDES
            logger.info("PHASE 3: Building slides...")
            for i, slide in enumerate(plan.slides, 1):
                logger.info(f"Building slide {i}: {slide.title}")
                
                await mcp_client.call_tool(
                    "ppt_server",
                    "add_slide",
                    {"layout_type": "title_and_content"}
                )
                
                await mcp_client.call_tool(
                    "ppt_server",
                    "write_text_to_slide",
                    {
                        "slide_index": i,
                        "title": slide.title,
                        "content": slide.bullet_points[:5]
                    }
                )
                
                logger.info(f"Slide {i} completed")
            
            # PHASE 4: APPLY THEME
            logger.info("PHASE 4: Applying theme...")
            await mcp_client.call_tool(
                "theme_server",
                "apply_theme",
                {"theme_name": "ocean"}
            )
            
            # PHASE 5: SAVE
            logger.info("PHASE 5: Saving presentation...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"output/presentation_{timestamp}.pptx"
            
            save_result = await mcp_client.call_tool(
                "ppt_server",
                "save_presentation",
                {"file_path": output_file}
            )
            
            if save_result and save_result.get("status") == "success":
                logger.info(f"Presentation saved: {output_file}")
                return {
                    "status": "success",
                    "file_path": output_file,
                    "num_slides": plan.num_slides
                }
            else:
                return {"status": "error", "message": "Failed to save"}
                
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def _create_default_plan(self, user_prompt: str) -> PresentationPlan:
        """Create presentation plan"""
        keywords = user_prompt.split()[:3]
        topic = " ".join(keywords)
        
        slides = [
            SlideStructure(
                index=1,
                title="Introduction",
                bullet_points=[f"Topic: {topic}", "Overview", "Key points"],
                include_image=False
            ),
            SlideStructure(
                index=2,
                title="Background",
                bullet_points=["Context", "History", "Importance"],
                include_image=False
            ),
            SlideStructure(
                index=3,
                title="Main Content",
                bullet_points=["Key point 1", "Key point 2", "Key point 3"],
                include_image=False
            ),
            SlideStructure(
                index=4,
                title="Analysis",
                bullet_points=["Finding 1", "Finding 2", "Implications"],
                include_image=False
            ),
            SlideStructure(
                index=5,
                title="Conclusion",
                bullet_points=["Summary", "Takeaways", "Next steps"],
                include_image=False
            )
        ]
        
        return PresentationPlan(
            title=f"Presentation on {topic}",
            subtitle=user_prompt[:60],
            num_slides=5,
            slides=slides
        )

agent_engine = None

def init_agent(hf_token: str = None):
    """Initialize agent"""
    global agent_engine
    agent_engine = AgentEngine(hf_token=hf_token)
    return agent_engine
