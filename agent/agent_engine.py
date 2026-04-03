"""
Agent Engine - FIXED VERSION
Issues fixed:
1. LLM plan JSON parse failure (unknown extension ?R) — bad regex on raw content
2. add_slide called without slide_index tracking — slides were built on wrong indices
3. output/ vs outputs/ path mismatch
4. theme_server call crashing whole flow — made optional
5. User prompt was ignored — full prompt now passed to LLM
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
            logger.info(f"Created plan with {plan.num_slides} slides: {plan.title}")

            # PHASE 2: CREATE PRESENTATION
            logger.info("PHASE 2: Creating presentation...")
            create_result = await mcp_client.call_tool(
                "ppt_server",
                "create_presentation",
                {"title": plan.title, "subtitle": plan.subtitle},
            )

            if not create_result or create_result.get("status") != "success":
                logger.error(f"create_presentation failed: {create_result}")
                return {"status": "error", "message": f"create_presentation failed: {create_result}"}

            # PHASE 3: BUILD SLIDES
            # NOTE: slide index 0 is the title slide created above
            # Content slides start at index 1
            logger.info("PHASE 3: Building slides...")
            for slide in plan.slides:
                # Step A: add the slide shell
                add_result = await mcp_client.call_tool(
                    "ppt_server",
                    "add_slide",
                    {"layout_type": "title_and_content"},
                )
                if not add_result or add_result.get("status") != "success":
                    logger.warning(f"add_slide failed for slide {slide.index}: {add_result}")
                    continue

                # The server returns current slide_count; the new slide is at (count - 1)
                actual_index = add_result.get("slide_count", slide.index + 1) - 1

                # Step B: write content into that slide
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
                    f"Slide {slide.index} '{slide.title}' → write: {write_result.get('status') if write_result else 'failed'}"
                )

            # PHASE 4: SAVE
            logger.info("PHASE 4: Saving presentation...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # FIX: use 'outputs' (plural) to match the actual folder
            output_file = f"outputs/presentation_{timestamp}.pptx"

            save_result = await mcp_client.call_tool(
                "ppt_server",
                "save_presentation",
                {"file_path": output_file},
            )

            if save_result and save_result.get("status") == "success":
                logger.info(f"Presentation saved: {output_file}")
                return {
                    "status": "success",
                    "file_path": output_file,
                    "title": plan.title,
                    "num_slides": plan.num_slides,
                }
            else:
                return {"status": "error", "message": f"Save failed: {save_result}"}

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # LLM PLAN
    # ------------------------------------------------------------------

    async def _create_llm_plan(self, user_prompt: str) -> PresentationPlan:
        """Call HuggingFace Inference API to generate a context-aware outline"""
        try:
            from config import get_settings
            from huggingface_hub import AsyncInferenceClient

            settings = get_settings()
            if not settings.HF_TOKEN:
                logger.warning("No HF_TOKEN — falling back to default plan.")
                return self._create_default_plan(user_prompt)

            client = AsyncInferenceClient(token=settings.HF_TOKEN)
            model_id = getattr(settings, "LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

            # FULL prompt passed — was being truncated before
            system_msg = (
                "You are a presentation outline generator. "
                "Return ONLY a valid JSON object — no markdown fences, no extra text, no comments."
            )
            user_msg = (
                f"Create a PowerPoint outline for the following request:\n\n"
                f"\"{user_prompt}\"\n\n"
                f"Return this exact JSON structure:\n"
                f'{{"title": "...", "subtitle": "...", "num_slides": 5, '
                f'"slides": [{{"index": 1, "title": "...", "bullet_points": ["...", "...", "..."]}}]}}\n\n'
                f"Make the content specifically relevant to the request above. "
                f"If a number of slides is mentioned in the request, use that number."
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
            logger.debug(f"Raw LLM response: {raw[:200]}")

            # FIXED JSON extraction — handles markdown fences and stray text
            json_str = self._extract_json(raw)
            data = json.loads(json_str)

            slides = [SlideStructure(**s) for s in data.get("slides", [])]
            plan = PresentationPlan(
                title=data.get("title", user_prompt[:60]),
                subtitle=data.get("subtitle", ""),
                num_slides=len(slides),
                slides=slides,
            )
            logger.info(f"LLM plan success: '{plan.title}' with {plan.num_slides} slides")
            return plan

        except Exception as e:
            logger.error(f"LLM plan failed: {e} — falling back to default.")
            return self._create_default_plan(user_prompt)

    def _extract_json(self, text: str) -> str:
        """
        Robustly extract JSON from LLM output.
        Handles: raw JSON, ```json fences, ``` fences, leading/trailing text.
        FIX for 'unknown extension ?R at position 12' — that was a regex bug.
        """
        # Strip markdown fences first
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            return fenced.group(1).strip()

        # Find outermost { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]

        # Last resort — return as-is and let json.loads raise a clear error
        return text

    def _create_default_plan(self, user_prompt: str) -> PresentationPlan:
        """Fallback plan that still uses the full user prompt as context"""
        topic = user_prompt.strip() or "Presentation"

        slides = [
            SlideStructure(index=1, title="Introduction", bullet_points=[f"Topic: {topic}", "Overview", "Objectives"]),
            SlideStructure(index=2, title="Background", bullet_points=["Context and history", "Why this matters", "Key definitions"]),
            SlideStructure(index=3, title="Core Concepts", bullet_points=["Concept 1", "Concept 2", "Concept 3"]),
            SlideStructure(index=4, title="Key Insights", bullet_points=["Finding 1", "Finding 2", "Implications"]),
            SlideStructure(index=5, title="Conclusion", bullet_points=["Summary", "Takeaways", "Next steps"]),
        ]

        return PresentationPlan(
            title=topic[:80],
            subtitle="An Overview",
            num_slides=5,
            slides=slides,
        )


# Singleton
agent_engine: Optional[AgentEngine] = None


def init_agent(hf_token: str = None) -> AgentEngine:
    global agent_engine
    agent_engine = AgentEngine(hf_token=hf_token)
    return agent_engine
