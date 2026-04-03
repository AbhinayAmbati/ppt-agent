"""
Agent Engine - Styled Version
- Picks a theme based on topic keywords
- Passes theme_name to create_presentation
- Removed broken separate theme_server call (styling now inside ppt_server)
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SlideStructure(BaseModel):
    index: int
    title: str
    bullet_points: List[str]
    include_image: bool = False


class PresentationPlan(BaseModel):
    title: str
    subtitle: str
    num_slides: int
    slides: List[SlideStructure]
    theme: str = "ocean"


def _pick_theme(prompt: str) -> str:
    """Pick a theme based on keywords in the user prompt."""
    prompt_lower = prompt.lower()
    if any(w in prompt_lower for w in ["science", "space", "ocean", "water", "nature", "biology"]):
        return "ocean"
    if any(w in prompt_lower for w in ["business", "finance", "corporate", "market", "sales", "strategy"]):
        return "corporate"
    if any(w in prompt_lower for w in ["history", "literature", "philosophy", "art", "culture", "university"]):
        return "academic"
    if any(w in prompt_lower for w in ["tech", "ai", "software", "code", "data", "cyber", "machine"]):
        return "dark"
    return "ocean"  # default


class AgentEngine:
    def __init__(self, hf_token: str = None):
        self.hf_token = hf_token
        logger.info("Agent Engine initialized")

    async def create_presentation(self, user_prompt: str, mcp_client) -> Dict[str, Any]:
        logger.info(f"Starting presentation creation: {user_prompt[:80]}...")

        try:
            # PHASE 1: PLAN
            logger.info("PHASE 1: Planning slide structure...")
            plan = await self._create_llm_plan(user_prompt)
            logger.info(f"Plan: '{plan.title}' | {plan.num_slides} slides | theme: {plan.theme}")

            # PHASE 2: CREATE PRESENTATION (with theme baked in)
            logger.info("PHASE 2: Creating presentation...")
            create_result = await mcp_client.call_tool(
                "ppt_server",
                "create_presentation",
                {
                    "title": plan.title,
                    "subtitle": plan.subtitle,
                    "theme_name": plan.theme,
                },
            )

            if not create_result or create_result.get("status") != "success":
                logger.error(f"create_presentation failed: {create_result}")
                return {"status": "error", "message": f"create_presentation failed: {create_result}"}

            # PHASE 3: BUILD SLIDES
            logger.info("PHASE 3: Building slides...")
            for slide in plan.slides:
                add_result = await mcp_client.call_tool(
                    "ppt_server",
                    "add_slide",
                    {"layout_type": "title_and_content"},
                )
                if not add_result or add_result.get("status") != "success":
                    logger.warning(f"add_slide failed for slide {slide.index}: {add_result}")
                    continue

                actual_index = add_result.get("slide_count", slide.index + 1) - 1

                write_result = await mcp_client.call_tool(
                    "ppt_server",
                    "write_text_to_slide",
                    {
                        "slide_index": actual_index,
                        "title": slide.title,
                        "content": slide.bullet_points[:5],
                    },
                )
                logger.info(
                    f"Slide {slide.index} '{slide.title}' → {write_result.get('status') if write_result else 'failed'}"
                )

            # PHASE 4: SAVE
            logger.info("PHASE 4: Saving presentation...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/presentation_{timestamp}.pptx"

            save_result = await mcp_client.call_tool(
                "ppt_server",
                "save_presentation",
                {"file_path": output_file},
            )

            if save_result and save_result.get("status") == "success":
                actual_path = save_result.get("file_path", output_file)
                filename = Path_basename(actual_path)
                logger.info(f"Presentation saved: {actual_path}")
                return {
                    "status": "success",
                    "file_path": filename,
                    "title": plan.title,
                    "num_slides": plan.num_slides,
                    "theme": plan.theme,
                }
            else:
                return {"status": "error", "message": f"Save failed: {save_result}"}

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def _create_llm_plan(self, user_prompt: str) -> PresentationPlan:
        try:
            from config import get_settings
            from huggingface_hub import AsyncInferenceClient

            settings = get_settings()
            if not settings.HF_TOKEN:
                logger.warning("No HF_TOKEN — falling back to default plan.")
                return self._create_default_plan(user_prompt)

            client = AsyncInferenceClient(token=settings.HF_TOKEN)
            model_id = getattr(settings, "LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

            system_msg = (
                "You are a presentation outline generator. "
                "Return ONLY a valid JSON object — no markdown fences, no extra text, no comments."
            )
            user_msg = (
                f"Create a PowerPoint outline for the following request:\n\n"
                f"\"{user_prompt}\"\n\n"
                f"Return this exact JSON structure:\n"
                f'{{"title": "...", "subtitle": "...", "num_slides": 5, '
                f'"slides": [{{"index": 1, "title": "...", "bullet_points": ["...", "...", "..."], "include_image": false}}]}}\n\n'
                f"Make the content specifically relevant to the request. "
                f"If a number of slides is mentioned, use that number. "
                f"Each slide must have 3-5 detailed bullet points."
            )

            logger.info(f"Querying LLM: {model_id}")
            response = await client.chat_completion(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=2000,
                temperature=0.5,
            )

            raw = response.choices[0].message.content.strip()
            json_str = self._extract_json(raw)
            data = json.loads(json_str)

            slides = [SlideStructure(**s) for s in data.get("slides", [])]
            theme = _pick_theme(user_prompt)

            plan = PresentationPlan(
                title=data.get("title", user_prompt[:60]),
                subtitle=data.get("subtitle", ""),
                num_slides=len(slides),
                slides=slides,
                theme=theme,
            )
            logger.info(f"LLM plan success: '{plan.title}' with {plan.num_slides} slides")
            return plan

        except Exception as e:
            logger.error(f"LLM plan failed: {e} — falling back to default.")
            return self._create_default_plan(user_prompt)

    def _extract_json(self, text: str) -> str:
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            return fenced.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start: end + 1]
        return text

    def _create_default_plan(self, user_prompt: str) -> PresentationPlan:
        topic = user_prompt.strip() or "Presentation"
        theme = _pick_theme(user_prompt)
        slides = [
            SlideStructure(index=1, title="Introduction",   bullet_points=[f"Overview of {topic}", "Goals and objectives", "Why this matters"]),
            SlideStructure(index=2, title="Background",     bullet_points=["Historical context", "Key developments", "Current landscape"]),
            SlideStructure(index=3, title="Core Concepts",  bullet_points=["Concept one explained", "Concept two explained", "How they connect"]),
            SlideStructure(index=4, title="Key Insights",   bullet_points=["Primary finding", "Secondary finding", "Broader implications"]),
            SlideStructure(index=5, title="Conclusion",     bullet_points=["Summary of key points", "Actionable takeaways", "Next steps"]),
        ]
        return PresentationPlan(
            title=topic[:80],
            subtitle="A Comprehensive Overview",
            num_slides=5,
            slides=slides,
            theme=theme,
        )


def Path_basename(path_str: str) -> str:
    from pathlib import Path
    return Path(path_str).name


agent_engine: Optional[AgentEngine] = None


def init_agent(hf_token: str = None) -> AgentEngine:
    global agent_engine
    agent_engine = AgentEngine(hf_token=hf_token)
    return agent_engine
