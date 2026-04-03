"""
Agent Engine
============
Orchestrates the full 5-phase agentic loop for Auto-PPT generation.

Phases
------
1. PLAN        — Calls Qwen/Qwen2.5-72B-Instruct via HuggingFace Inference API
                 to generate a structured JSON slide outline from the user prompt.
2. WEB SEARCH  — For each slide, queries web_search_server (DuckDuckGo) to inject
                 1-2 real factual sentences into bullet points.
                 Every 3rd slide is flagged for an image placeholder.
3. CREATE      — Calls ppt_server.create_presentation with title, subtitle, theme.
4. BUILD       — Iterates slides: add_slide → write_text_to_slide per slide.
                 Last slide rendered as special conclusion layout.
5. SAVE        — Calls ppt_server.save_presentation → outputs/ folder.

MCP Servers Used
----------------
- ppt_server        (1.ppt_server.py)        : PPT file creation and styling
- web_search_server (2.web_search_server.py) : DuckDuckGo text search for enrichment

Theme Selection
---------------
Auto-picks from: ocean | corporate | academic | dark
based on keywords in the user prompt. Defaults to ocean.

Error Handling
--------------
All phases fall back gracefully — LLM failure → default plan,
search failure → LLM bullets used as-is. Never crashes the request.
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


class SlideStructure(BaseModel):
    """Single slide definition produced by the LLM plan."""
    index: int
    title: str
    bullet_points: List[str]
    include_image: bool = False  # True → two-column layout with styled placeholder


class PresentationPlan(BaseModel):
    """Full presentation plan output by _create_llm_plan."""
    title: str
    subtitle: str
    num_slides: int
    slides: List[SlideStructure]
    theme: str = "ocean"


def _sanitize_bullets(bullets: list) -> List[str]:
    """
    Coerce any bullet value to a clean string.
    Handles: plain str, dict (LLM sometimes returns objects), None.
    """
    result = []
    for b in bullets:
        if isinstance(b, str):
            clean = b.strip()
        elif isinstance(b, dict):
            clean = str(b.get("text", b.get("content", str(b)))).strip()
        elif b is None:
            continue
        else:
            clean = str(b).strip()
        if clean:
            result.append(clean)
    return result


def _pick_theme(prompt: str) -> str:
    """
    Auto-select a visual theme based on topic keywords in the user prompt.

    Mapping:
      ocean     — science, space, nature, biology, environment
      corporate — business, finance, market, sales, strategy, marketing
      academic  — history, literature, philosophy, art, culture, education
      dark      — tech, AI, software, code, data, cyber, cloud, programming
      ocean     — default fallback
    """
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


class AgentEngine:
    """
    Main orchestrator for the Auto-PPT agentic loop.

    Usage
    -----
    engine = AgentEngine(hf_token="hf_...")
    result = await engine.create_presentation("5 slides on Machine Learning", mcp_client)
    # result = {"status": "success", "file_path": "presentation_20260403.pptx", ...}
    """

    def __init__(self, hf_token: str = None):
        self.hf_token = hf_token
        logger.info("Agent Engine initialized")

    async def create_presentation(self, user_prompt: str, mcp_client) -> Dict[str, Any]:
        """
        Entry point. Runs the full 5-phase pipeline.

        Parameters
        ----------
        user_prompt : str
            Raw user input e.g. "Create a 6-slide PPT on Artificial Intelligence"
        mcp_client  : MCPClient
            Live MCP client instance with ppt_server and web_search_server available.

        Returns
        -------
        dict
            {"status": "success", "file_path": "...", "title": "...", "num_slides": N, "theme": "..."}
            or {"status": "error", "message": "..."}
        """
        logger.info(f"[AGENT] Starting: {user_prompt[:80]}...")

        try:
            # PHASE 1: PLAN
            logger.info("[PHASE 1] Planning slide structure with LLM...")
            plan = await self._create_llm_plan(user_prompt)
            logger.info(f"[PHASE 1] '{plan.title}' | {plan.num_slides} slides | theme={plan.theme}")

            # PHASE 2: WEB SEARCH — enrich bullets with real facts
            logger.info("[PHASE 2] Enriching slides with web search...")
            plan = await self._enrich_with_search(plan, mcp_client)

            # PHASE 3: CREATE PRESENTATION
            logger.info("[PHASE 3] Creating presentation file...")
            create_result = await mcp_client.call_tool(
                "ppt_server", "create_presentation",
                {"title": plan.title, "subtitle": plan.subtitle, "theme_name": plan.theme},
            )
            if not create_result or create_result.get("status") != "success":
                return {"status": "error", "message": f"create_presentation failed: {create_result}"}

            # PHASE 4: BUILD SLIDES
            logger.info("[PHASE 4] Building slides...")
            total = len(plan.slides)
            for slide in plan.slides:
                add_result = await mcp_client.call_tool(
                    "ppt_server", "add_slide", {"layout_type": "title_and_content"}
                )
                if not add_result or add_result.get("status") != "success":
                    logger.warning(f"  add_slide failed for slide {slide.index}")
                    continue

                actual_index  = add_result.get("slide_count", slide.index + 1) - 1
                is_last       = (slide.index == total)
                clean_bullets = _sanitize_bullets(slide.bullet_points) or [f"Key points about {slide.title}"]

                write_result = await mcp_client.call_tool(
                    "ppt_server", "write_text_to_slide",
                    {
                        "slide_index":   actual_index,
                        "title":         str(slide.title).strip(),
                        "content":       clean_bullets[:5],
                        "include_image": bool(slide.include_image),
                        "is_conclusion": bool(is_last),
                    },
                )
                logger.info(
                    f"  Slide {slide.index}/{total} '{slide.title}' "
                    f"[img_placeholder={slide.include_image}, conclusion={is_last}] "
                    f"→ {write_result.get('status') if write_result else 'FAILED'}"
                )

            # PHASE 5: SAVE
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

    async def _enrich_with_search(self, plan: PresentationPlan, mcp_client) -> PresentationPlan:
        """
        Phase 2: Web search enrichment.

        For each slide:
        - Searches DuckDuckGo for "{presentation title} {slide title}"
        - Extracts the first sentence of up to 2 snippets as real facts
        - Prepends facts to LLM bullet points (max 5 bullets total)
        - Sets include_image=True on every 3rd slide for a styled placeholder

        Falls back silently — if search fails, LLM bullets are used unchanged.
        """
        enriched = []
        for slide in plan.slides:
            if slide.index % 3 == 0:
                slide = slide.model_copy(update={"include_image": True})

            query = f"{plan.title} {slide.title}"
            logger.info(f"  [SEARCH] '{query}'")

            search_result = await mcp_client.call_tool(
                "web_search_server", "search_topic",
                {"query": query, "max_results": 3},
            )

            if search_result and search_result.get("status") == "success":
                facts = []
                for r in search_result.get("results", [])[:2]:
                    snippet = r.get("snippet", "").strip()
                    if len(snippet) > 20:
                        sentence = snippet.split(".")[0].strip()[:120]
                        if sentence:
                            facts.append(sentence)
                if facts:
                    existing = _sanitize_bullets(slide.bullet_points)
                    slide = slide.model_copy(update={"bullet_points": (facts + existing)[:5]})
                    logger.info(f"  [SEARCH] Injected {len(facts)} facts into '{slide.title}'")
                else:
                    logger.info(f"  [SEARCH] No usable snippets for '{slide.title}'")
            else:
                logger.warning(f"  [SEARCH] Failed for '{slide.title}'")

            enriched.append(slide)

        return plan.model_copy(update={"slides": enriched})

    async def _create_llm_plan(self, user_prompt: str) -> PresentationPlan:
        """
        Phase 1: Generate slide outline via HuggingFace Inference API.

        Model   : Qwen/Qwen2.5-72B-Instruct (configurable via LLM_MODEL in .env)
        Output  : PresentationPlan with title, subtitle, slides[], theme
        Fallback: _create_default_plan() if HF_TOKEN missing or API call fails
        """
        try:
            from config import get_settings
            from huggingface_hub import AsyncInferenceClient

            settings = get_settings()
            if not settings.HF_TOKEN:
                return self._create_default_plan(user_prompt)

            client   = AsyncInferenceClient(token=settings.HF_TOKEN)
            model_id = getattr(settings, "LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

            system_msg = (
                "You are a presentation outline generator. "
                "Return ONLY a valid JSON object — no markdown fences, no comments, no extra text. "
                "All bullet_points must be plain strings."
            )
            user_msg = (
                f"Create a PowerPoint outline for:\n\n\"{user_prompt}\"\n\n"
                f"Return this JSON:\n"
                f'{{"title":"...","subtitle":"...","num_slides":5,'
                f'"slides":[{{"index":1,"title":"...","bullet_points":["...","...","..."],"include_image":false}}]}}\n\n'
                f"Rules:\n"
                f"- Use exact slide count if mentioned in the request.\n"
                f"- 3-5 specific factual bullet points per slide as plain strings.\n"
                f"- Last slide titled 'Conclusion' or 'Key Takeaways'.\n"
                f"- Set include_image true on 1-2 slides where a diagram would help.\n"
                f"- Content must be specifically about the requested topic."
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

            raw_slides = data.get("slides", [])
            for s in raw_slides:
                s["bullet_points"] = _sanitize_bullets(s.get("bullet_points", []))

            slides = [SlideStructure(**s) for s in raw_slides]
            return PresentationPlan(
                title     = data.get("title", user_prompt[:60]),
                subtitle  = data.get("subtitle", ""),
                num_slides= len(slides),
                slides    = slides,
                theme     = _pick_theme(user_prompt),
            )

        except Exception as e:
            logger.error(f"LLM plan failed: {e} — using default.")
            return self._create_default_plan(user_prompt)

    def _extract_json(self, text: str) -> str:
        """
        Robustly extract a JSON object from raw LLM output.
        Handles: plain JSON, ```json fenced blocks, leading/trailing prose.
        """
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            return fenced.group(1).strip()
        start = text.find("{")
        end   = text.rfind("}")
        if start != -1 and end > start:
            return text[start: end + 1]
        return text

    def _create_default_plan(self, user_prompt: str) -> PresentationPlan:
        """
        Fallback plan used when HF_TOKEN is missing or the LLM call fails.
        Generates a generic 5-slide structure using the user prompt as topic context.
        Slide 3 always includes an image placeholder.
        """
        topic = user_prompt.strip() or "Topic"
        slides = [
            SlideStructure(index=1, title="Introduction",
                           bullet_points=[f"Overview of {topic}", "Goals and objectives", "Why this matters"]),
            SlideStructure(index=2, title="Background & Context",
                           bullet_points=["Historical context", "Key developments", "Current landscape"]),
            SlideStructure(index=3, title="Core Concepts",
                           bullet_points=["Concept 1 explained", "Concept 2 explained", "How they connect"],
                           include_image=True),
            SlideStructure(index=4, title="Key Insights",
                           bullet_points=["Primary finding", "Secondary finding", "Broader implications"]),
            SlideStructure(index=5, title="Conclusion",
                           bullet_points=["Summary of key points", "Actionable takeaways", "Next steps"]),
        ]
        return PresentationPlan(
            title="A Comprehensive Overview", subtitle=topic[:80],
            num_slides=5, slides=slides, theme=_pick_theme(user_prompt),
        )


# ── SINGLETON ─────────────────────────────────────────────────────────────────

agent_engine: Optional[AgentEngine] = None


def init_agent(hf_token: str = None) -> AgentEngine:
    """
    Initialize the global AgentEngine singleton.
    Called once at FastAPI startup via the @app.on_event("startup") handler.
    """
    global agent_engine
    agent_engine = AgentEngine(hf_token=hf_token)
    return agent_engine
