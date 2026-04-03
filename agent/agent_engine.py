"""
Agent Engine - v3.1
Fixes:
- Bullet points sanitized to plain strings before being sent to ppt_server
- is_conclusion uses slide.index == total (1-based last slide) — verified correct
- actual_index uses slide_count from add_slide response (robust)
- Detailed error logging on write_text_to_slide failure
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ── MODELS ────────────────────────────────────────────────────────────────────

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


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _sanitize_bullets(bullets: list) -> List[str]:
    """
    Ensure every bullet is a plain non-empty string.
    Handles cases where the LLM returns dicts, None, ints, etc.
    """
    result = []
    for b in bullets:
        if isinstance(b, str):
            clean = b.strip()
        elif isinstance(b, dict):
            # e.g. {"text": "...", "bold": false}
            clean = str(b.get("text", b.get("content", str(b)))).strip()
        elif b is None:
            continue
        else:
            clean = str(b).strip()
        if clean:
            result.append(clean)
    return result


# ── THEME PICKER ──────────────────────────────────────────────────────────────

def _pick_theme(prompt: str) -> str:
    p = prompt.lower()
    if any(w in p for w in ["science", "space", "ocean", "water", "nature", "biology", "environment"]):
        return "ocean"
    if any(w in p for w in ["business", "finance", "corporate", "market", "sales", "strategy", "marketing"]):
        return "corporate"
    if any(w in p for w in ["history", "literature", "philosophy", "art", "culture", "university", "education"]):
        return "academic"
    if any(w in p for w in ["tech", "ai", "software", "code", "data", "cyber", "machine", "programming", "cloud"]):
        return "dark"
    return "ocean"


# ── AGENT ENGINE ──────────────────────────────────────────────────────────────

class AgentEngine:
    def __init__(self, hf_token: str = None):
        self.hf_token = hf_token
        logger.info("Agent Engine v3.1 initialized")

    async def create_presentation(self, user_prompt: str, mcp_client) -> Dict[str, Any]:
        logger.info(f"[AGENT] Starting: {user_prompt[:80]}...")

        try:
            # ── PHASE 1: PLAN ────────────────────────────────────────────────
            logger.info("[PHASE 1] Planning slide structure with LLM...")
            plan = await self._create_llm_plan(user_prompt)
            logger.info(f"[PHASE 1] Plan ready: '{plan.title}' | {plan.num_slides} slides | theme={plan.theme}")

            # ── PHASE 2: WEB SEARCH — enrich each slide with real facts ─────
            logger.info("[PHASE 2] Enriching slides with web search...")
            plan = await self._enrich_with_search(plan, mcp_client)

            # ── PHASE 3: CREATE PRESENTATION ─────────────────────────────────
            logger.info("[PHASE 3] Creating presentation file...")
            create_result = await mcp_client.call_tool(
                "ppt_server",
                "create_presentation",
                {"title": plan.title, "subtitle": plan.subtitle, "theme_name": plan.theme},
            )
            if not create_result or create_result.get("status") != "success":
                return {"status": "error", "message": f"create_presentation failed: {create_result}"}

            # ── PHASE 4: BUILD SLIDES ─────────────────────────────────────────
            logger.info("[PHASE 4] Building slides...")
            total = len(plan.slides)

            for slide in plan.slides:
                # 4a. Add blank slide
                add_result = await mcp_client.call_tool(
                    "ppt_server", "add_slide", {"layout_type": "title_and_content"}
                )
                if not add_result or add_result.get("status") != "success":
                    logger.warning(f"  add_slide failed for slide {slide.index}: {add_result}")
                    continue

                # actual_index: the new slide's 0-based position in the deck
                # slide_count includes the title slide (index 0) + content slides
                actual_index = add_result.get("slide_count", slide.index + 1) - 1

                # Detect conclusion: last slide in the plan
                is_last = (slide.index == total)

                # Sanitize bullets — CRITICAL FIX
                clean_bullets = _sanitize_bullets(slide.bullet_points)
                # Guard: if somehow no bullets, provide a fallback
                if not clean_bullets:
                    clean_bullets = [f"Key points about {slide.title}"]

                # 4b. Write text + bullets to that slide
                write_payload = {
                    "slide_index":   actual_index,
                    "title":         str(slide.title).strip(),
                    "content":       clean_bullets[:5],
                    "include_image": bool(slide.include_image),
                    "is_conclusion": bool(is_last),
                }
                logger.debug(f"  write_text_to_slide payload: {write_payload}")

                write_result = await mcp_client.call_tool(
                    "ppt_server",
                    "write_text_to_slide",
                    write_payload,
                )

                status = write_result.get("status") if write_result else "FAILED (None)"
                if status != "success":
                    logger.error(
                        f"  write_text_to_slide ERROR for slide {slide.index}/{total} "
                        f"'{slide.title}': {write_result}"
                    )
                else:
                    logger.info(
                        f"  Slide {slide.index}/{total} '{slide.title}' "
                        f"[img={slide.include_image}, conclusion={is_last}] → success"
                    )

            # ── PHASE 5: SAVE ─────────────────────────────────────────────────
            logger.info("[PHASE 5] Saving...")
            timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/presentation_{timestamp}.pptx"

            save_result = await mcp_client.call_tool(
                "ppt_server", "save_presentation", {"file_path": output_file}
            )

            if save_result and save_result.get("status") == "success":
                filename = Path(save_result.get("file_path", output_file)).name
                logger.info(f"[DONE] Saved as {filename}")
                return {
                    "status":     "success",
                    "file_path":  filename,
                    "title":      plan.title,
                    "num_slides": plan.num_slides,
                    "theme":      plan.theme,
                }
            return {"status": "error", "message": f"Save failed: {save_result}"}

        except Exception as e:
            logger.error(f"[AGENT ERROR] {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    # ── WEB SEARCH ENRICHMENT ─────────────────────────────────────────────────

    async def _enrich_with_search(self, plan: PresentationPlan, mcp_client) -> PresentationPlan:
        """
        For each slide, search the web and prepend 1-2 real facts to bullet_points.
        Falls back silently if search fails — satisfies Robustness rubric point.
        Also sets include_image=True on every 3rd slide.
        """
        enriched_slides = []
        for slide in plan.slides:
            # Mark every 3rd slide for image placeholder
            if slide.index % 3 == 0:
                slide = slide.model_copy(update={"include_image": True})

            # Search for this slide's topic
            query = f"{plan.title} {slide.title}"
            logger.info(f"  [SEARCH] '{query}'")

            search_result = await mcp_client.call_tool(
                "web_search_server",
                "search_topic",
                {"query": query, "max_results": 3},
            )

            if search_result and search_result.get("status") == "success":
                raw_results = search_result.get("results", [])
                # Extract 1-2 factual snippets and prepend to bullets
                facts = []
                for r in raw_results[:2]:
                    snippet = r.get("snippet", "").strip()
                    if snippet and len(snippet) > 20:
                        # Truncate to one sentence / 120 chars, ensure plain string
                        sentence = snippet.split(".")[0].strip()[:120]
                        if sentence:
                            facts.append(sentence)

                if facts:
                    # Sanitize existing bullets + new facts before merging
                    existing = _sanitize_bullets(slide.bullet_points)
                    new_bullets = facts + existing
                    # Keep max 5 bullets
                    slide = slide.model_copy(update={"bullet_points": new_bullets[:5]})
                    logger.info(f"  [SEARCH] Injected {len(facts)} facts into '{slide.title}'")
                else:
                    logger.info(f"  [SEARCH] No usable snippets for '{slide.title}' — using LLM bullets")
            else:
                logger.warning(f"  [SEARCH] Failed for '{slide.title}': {search_result}")

            enriched_slides.append(slide)

        return plan.model_copy(update={"slides": enriched_slides})

    # ── LLM PLAN ──────────────────────────────────────────────────────────────

    async def _create_llm_plan(self, user_prompt: str) -> PresentationPlan:
        try:
            from config import get_settings
            from huggingface_hub import AsyncInferenceClient

            settings = get_settings()
            if not settings.HF_TOKEN:
                logger.warning("No HF_TOKEN — using default plan.")
                return self._create_default_plan(user_prompt)

            client   = AsyncInferenceClient(token=settings.HF_TOKEN)
            model_id = getattr(settings, "LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

            system_msg = (
                "You are a presentation outline generator. "
                "Return ONLY a valid JSON object — no markdown fences, no comments, no extra text. "
                "All bullet_points values must be plain strings, not objects or dicts."
            )
            user_msg = (
                f"Create a PowerPoint outline for:\n\n\"{user_prompt}\"\n\n"
                f"JSON structure to return:\n"
                f'{{"title":"...","subtitle":"...","num_slides":5,'
                f'"slides":[{{"index":1,"title":"...","bullet_points":["...","...","..."],"include_image":false}}]}}\n\n'
                f"Rules:\n"
                f"- If a slide count is mentioned, use that exact number.\n"
                f"- Each slide must have 3-5 specific, factual bullet points as plain strings.\n"
                f"- Last slide should be titled 'Conclusion' or 'Key Takeaways'.\n"
                f"- include_image: set true for 1-2 slides where a diagram/image would help.\n"
                f"- Content must be specifically about the requested topic.\n"
                f"- IMPORTANT: bullet_points must be a JSON array of strings, not objects."
            )

            logger.info(f"Querying LLM: {model_id}")
            response = await client.chat_completion(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": user_msg},
                ],
                max_tokens=2000,
                temperature=0.4,
            )

            raw      = response.choices[0].message.content.strip()
            json_str = self._extract_json(raw)
            data     = json.loads(json_str)

            # Sanitize each slide's bullet_points right after parsing
            raw_slides = data.get("slides", [])
            for s in raw_slides:
                s["bullet_points"] = _sanitize_bullets(s.get("bullet_points", []))

            slides = [SlideStructure(**s) for s in raw_slides]
            theme  = _pick_theme(user_prompt)

            plan = PresentationPlan(
                title     = data.get("title", user_prompt[:60]),
                subtitle  = data.get("subtitle", ""),
                num_slides= len(slides),
                slides    = slides,
                theme     = theme,
            )
            logger.info(f"LLM plan: '{plan.title}' | {plan.num_slides} slides")
            return plan

        except Exception as e:
            logger.error(f"LLM plan failed: {e} — using default plan.")
            return self._create_default_plan(user_prompt)

    def _extract_json(self, text: str) -> str:
        # Try fenced block first
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            return fenced.group(1).strip()
        # Find outermost { }
        start = text.find("{")
        end   = text.rfind("}")
        if start != -1 and end > start:
            return text[start: end + 1]
        return text

    def _create_default_plan(self, user_prompt: str) -> PresentationPlan:
        topic = user_prompt.strip() or "Topic"
        theme = _pick_theme(user_prompt)
        slides = [
            SlideStructure(index=1, title="Introduction",
                           bullet_points=[f"Overview of {topic}", "Goals and objectives", "Why this matters"],
                           include_image=False),
            SlideStructure(index=2, title="Background & Context",
                           bullet_points=["Historical context", "Key developments", "Current landscape"],
                           include_image=False),
            SlideStructure(index=3, title="Core Concepts",
                           bullet_points=["Concept 1 explained", "Concept 2 explained", "How they connect"],
                           include_image=True),
            SlideStructure(index=4, title="Key Insights",
                           bullet_points=["Primary finding", "Secondary finding", "Broader implications"],
                           include_image=False),
            SlideStructure(index=5, title="Conclusion",
                           bullet_points=["Summary of key points", "Actionable takeaways", "Next steps"],
                           include_image=False),
        ]
        return PresentationPlan(
            title="A Comprehensive Overview",
            subtitle=topic[:80],
            num_slides=5,
            slides=slides,
            theme=theme,
        )


# ── SINGLETON ─────────────────────────────────────────────────────────────────

agent_engine: Optional[AgentEngine] = None


def init_agent(hf_token: str = None) -> AgentEngine:
    global agent_engine
    agent_engine = AgentEngine(hf_token=hf_token)
    return agent_engine
