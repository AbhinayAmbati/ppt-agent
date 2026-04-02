"""
LLM Client: Qwen model for prompt planning
Generates structured slide outline from user prompt
"""

import json
import logging
from typing import Optional
from dataclasses import dataclass
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SlideSpec:
    """Specification for a single slide"""
    title: str
    bullet_points: list[str]  # 3-5 bullet points
    search_query: Optional[str] = None  # What to search for content
    layout_type: str = "title_and_content"  # "title_and_content" or "title_only"


@dataclass
class PresentationPlan:
    """Complete presentation plan: 5 slides"""
    slides: list[SlideSpec]
    theme: str = "default"


class LLMClient:
    """Wrapper for HuggingFace Qwen model"""

    def __init__(self):
        """Initialize LLM client and load model"""
        self.model = None
        self.tokenizer = None
        self.device = settings.DEVICE
        self._load_model()

    def _load_model(self):
        """Load Qwen model from HuggingFace"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            logger.info(f"Loading {settings.LLM_MODEL} from HuggingFace...")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_MODEL,
                token=settings.HF_TOKEN if settings.HF_TOKEN else None,
                trust_remote_code=True
            )

            # Load model with reduced precision if CUDA available
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info("Loading model in fp16 for CUDA...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.LLM_MODEL,
                    token=settings.HF_TOKEN if settings.HF_TOKEN else None,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                logger.info("Loading model in full precision (CPU)...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.LLM_MODEL,
                    token=settings.HF_TOKEN if settings.HF_TOKEN else None,
                    trust_remote_code=True
                ).to(self.device)

            logger.info(f"Model loaded successfully on device: {self.device}")

        except ImportError as e:
            logger.error(f"Failed to import transformers: {e}")
            logger.warning("Using fallback mock LLM")
            self.model = None
            self.tokenizer = None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning("Using fallback mock LLM")
            self.model = None
            self.tokenizer = None

    def plan_presentation(self, prompt: str) -> PresentationPlan:
        """
        Generate a 5-slide presentation plan from user prompt
        Uses LLM to understand prompt and create structured outline
        """
        if not self.model or not self.tokenizer:
            logger.warning("Using mock planning (model not loaded)")
            return self._mock_plan(prompt)

        try:
            # Create structured prompt for planning
            planning_prompt = f"""
You are a PowerPoint presentation expert. Create a detailed 5-slide presentation outline based on this topic:

Topic: {prompt}

Return a JSON object with this exact structure:
{{
    "slides": [
        {{
            "title": "Slide 1 Title",
            "bullet_points": ["Point 1", "Point 2", "Point 3", "Point 4"],
            "search_query": "Optional search query for content"
        }},
        ... (repeat for 5 slides total)
    ],
    "theme": "default"  # or "ocean", "forest", "sunset", "midnight"
}}

Create slides that are informative, well-structured, and easy to understand.
"""

            # Tokenize input
            inputs = self.tokenizer(planning_prompt, return_tensors="pt").to(self.device)

            # Generate output
            outputs = self.model.generate(
                **inputs,
                max_length=2000,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

            # Decode output
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract JSON from response
            plan_json = self._extract_json_from_response(response)
            if not plan_json:
                logger.warning("Could not extract JSON from LLM response, using mock plan")
                return self._mock_plan(prompt)

            # Parse and validate
            return self._parse_plan_json(plan_json)

        except Exception as e:
            logger.error(f"Error in planning: {e}")
            logger.warning("Falling back to mock plan")
            return self._mock_plan(prompt)

    def _extract_json_from_response(self, response: str) -> Optional[dict]:
        """Extract JSON object from LLM response"""
        try:
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        return None

    def _parse_plan_json(self, plan_json: dict) -> PresentationPlan:
        """Parse and validate plan JSON"""
        try:
            slides = []
            for slide_data in plan_json.get("slides", [])[:5]:  # Max 5 slides
                slide = SlideSpec(
                    title=slide_data.get("title", "Slide"),
                    bullet_points=slide_data.get("bullet_points", []),
                    search_query=slide_data.get("search_query"),
                    layout_type=slide_data.get("layout_type", "title_and_content")
                )
                # Ensure at least 1 bullet point, max 5
                if not slide.bullet_points:
                    slide.bullet_points = ["Key information"]
                slide.bullet_points = slide.bullet_points[:5]
                slides.append(slide)

            # Ensure 5 slides
            while len(slides) < 5:
                slides.append(SlideSpec(
                    title="Additional Information",
                    bullet_points=["More details about the topic"]
                ))

            theme = plan_json.get("theme", "default")
            return PresentationPlan(slides=slides, theme=theme)

        except Exception as e:
            logger.error(f"Error parsing plan JSON: {e}")
            return self._mock_plan("Unable to parse")

    def _mock_plan(self, prompt: str) -> PresentationPlan:
        """Fallback: Generate a mock plan based on prompt"""
        logger.info(f"Generating mock plan for: {prompt}")

        slides = [
            SlideSpec(
                title="Introduction",
                bullet_points=[
                    f"Overview of {prompt.split()[0] if prompt else 'the topic'}",
                    "Key objectives and scope",
                    "What you will learn"
                ],
                search_query=prompt if prompt else "introduction"
            ),
            SlideSpec(
                title="Background & Context",
                bullet_points=[
                    "Historical development",
                    "Current state and relevance",
                    "Industry trends"
                ],
                search_query=f"{prompt} background" if prompt else "background"
            ),
            SlideSpec(
                title="Key Concepts",
                bullet_points=[
                    "Core principle 1",
                    "Core principle 2",
                    "Core principle 3",
                    "Implementation considerations"
                ],
                search_query=f"{prompt} concepts" if prompt else "concepts"
            ),
            SlideSpec(
                title="Practical Applications",
                bullet_points=[
                    "Use case 1",
                    "Use case 2",
                    "Benefits and advantages",
                    "Real-world examples"
                ],
                search_query=f"{prompt} applications" if prompt else "applications"
            ),
            SlideSpec(
                title="Summary & Conclusion",
                bullet_points=[
                    "Key takeaways",
                    "Future outlook",
                    "Call to action",
                    "Resources for learning more"
                ],
                search_query=f"{prompt} summary" if prompt else "summary"
            )
        ]

        return PresentationPlan(slides=slides, theme="default")


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
