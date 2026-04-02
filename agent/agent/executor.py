"""
Executor: Main agentic loop that generates PPT from slide plan
Coordinates MCP servers for slide creation, web search, theming
"""

import logging
import uuid
from typing import Optional
from agent.llm_client import PresentationPlan, SlideSpec
from agent.mcp_client import MCPClientPool, ToolResult
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PPTExecutor:
    """Executes presentation generation from plan"""

    def __init__(self, mcp_pool: MCPClientPool):
        self.mcp_pool = mcp_pool
        self.presentation_id = str(uuid.uuid4())

    async def execute_plan(self, plan: PresentationPlan, user_id: int) -> dict:
        """Execute presentation plan: create PPT with all slides"""
        logger.info(f"Starting presentation generation for user {user_id}")

        try:
            # Phase 1: Create presentation
            result = await self.mcp_pool.call_tool(
                "ppt",
                "create_presentation",
                {"title": "Auto-Generated Presentation", "subtitle": ""}
            )

            if not result.is_success:
                logger.error(f"Failed to create presentation: {result.error}")
                return {
                    "status": "error",
                    "message": "Failed to create presentation",
                    "presentation_id": self.presentation_id
                }

            # Phase 2: Apply theme
            logger.info(f"Applying theme: {plan.theme}")
            await self.mcp_pool.call_tool(
                "theme",
                "apply_theme",
                {"theme_name": plan.theme}
            )

            # Phase 3: Generate each slide
            for idx, slide in enumerate(plan.slides):
                logger.info(f"Generating slide {idx + 1}/5: {slide.title}")

                # Search for content if needed
                bullet_points = slide.bullet_points
                if slide.search_query:
                    search_result = await self.mcp_pool.call_tool(
                        "web_search",
                        "search_topic",
                        {"topic": slide.search_query, "max_results": 3}
                    )

                    if search_result.is_success:
                        # Extract content from search results
                        search_content = self._extract_content_from_search(search_result.data)
                        # Merge with original bullet points
                        bullet_points = slide.bullet_points + search_content[:2]  # Add top 2 results
                    else:
                        logger.warning(f"Search failed for {slide.search_query}, using default content")

                # Add slide to presentation
                add_result = await self.mcp_pool.call_tool(
                    "ppt",
                    "add_slide",
                    {"layout_type": slide.layout_type}
                )

                if not add_result.is_success:
                    logger.error(f"Failed to add slide {idx + 1}")
                    continue

                # Write content to slide
                write_result = await self.mcp_pool.call_tool(
                    "ppt",
                    "write_text_to_slide",
                    {
                        "slide_index": idx + 1,
                        "title": slide.title,
                        "content": bullet_points[:5]  # Max 5 bullet points
                    }
                )

                if not write_result.is_success:
                    logger.error(f"Failed to write text to slide {idx + 1}")

            # Phase 4: Save presentation
            file_name = f"presentation_{self.presentation_id}.pptx"
            file_path = f"{settings.OUTPUT_DIR}/{file_name}"

            save_result = await self.mcp_pool.call_tool(
                "ppt",
                "save_presentation",
                {"file_path": file_path}
            )

            if not save_result.is_success:
                logger.error(f"Failed to save presentation: {save_result.error}")
                return {
                    "status": "error",
                    "message": "Failed to save presentation",
                    "presentation_id": self.presentation_id
                }

            logger.info(f"Presentation generated successfully: {file_path}")

            return {
                "status": "success",
                "message": "Presentation generated successfully",
                "presentation_id": self.presentation_id,
                "file_path": file_path,
                "file_name": file_name,
                "slides_count": len(plan.slides)
            }

        except Exception as e:
            logger.error(f"Error executing plan: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "presentation_id": self.presentation_id
            }

    def _extract_content_from_search(self, search_data: dict) -> list[str]:
        """Extract bullet points from search results"""
        content = []
        try:
            results = search_data.get("results", [])
            for result in results[:2]:  # Take top 2 results
                title = result.get("title", "")
                body = result.get("body", "")[:100]  # Truncate to 100 chars
                if title:
                    content.append(f"{title} - {body}")
        except Exception as e:
            logger.warning(f"Error extracting search content: {e}")
        return content


class JobQueue:
    """Simple in-memory job queue for async PPT generation"""

    def __init__(self, max_concurrent: int = settings.MAX_CONCURRENT_JOBS):
        self.jobs: dict[str, dict] = {}
        self.max_concurrent = max_concurrent
        self.semaphore = None

    async def init(self):
        """Initialize semaphore for concurrency control"""
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    async def queue_job(
        self,
        job_id: str,
        user_id: int,
        prompt: str,
        llm_client,
        mcp_pool: MCPClientPool
    ):
        """Queue a PPT generation job"""
        import asyncio

        # Initialize job status
        self.jobs[job_id] = {
            "id": job_id,
            "user_id": user_id,
            "prompt": prompt,
            "status": "PENDING",
            "progress": 0,
            "result": None
        }

        # Run job with semaphore (max 3 concurrent)
        async with self.semaphore:
            await self._execute_job(job_id, user_id, prompt, llm_client, mcp_pool)

    async def _execute_job(
        self,
        job_id: str,
        user_id: int,
        prompt: str,
        llm_client,
        mcp_pool: MCPClientPool
    ):
        """Execute a single job"""
        import asyncio

        try:
            job = self.jobs[job_id]
            job["status"] = "RUNNING"
            job["progress"] = 10

            logger.info(f"[Job {job_id}] Starting presentation generation")

            # Phase 1: Planning
            logger.info(f"[Job {job_id}] Planning phase...")
            plan = llm_client.plan_presentation(prompt)
            job["progress"] = 30

            # Phase 2: Execution
            logger.info(f"[Job {job_id}] Execution phase...")
            executor = PPTExecutor(mcp_pool)
            result = await executor.execute_plan(plan, user_id)
            job["progress"] = 90

            # Update job with result
            job["status"] = "COMPLETED" if result["status"] == "success" else "FAILED"
            job["result"] = result
            job["progress"] = 100

            logger.info(f"[Job {job_id}] Completed: {result['status']}")

        except Exception as e:
            logger.error(f"[Job {job_id}] Failed: {e}", exc_info=True)
            job["status"] = "FAILED"
            job["result"] = {
                "status": "error",
                "message": str(e)
            }
            job["progress"] = 100

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        return self.jobs.get(job_id)

    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """Remove completed jobs older than max_age"""
        import time
        current_time = time.time()
        to_delete = []

        for job_id, job in self.jobs.items():
            if job["status"] in ["COMPLETED", "FAILED"]:
                # Could add timestamp if needed
                # For now, just keep all
                pass

        for job_id in to_delete:
            del self.jobs[job_id]


# Singleton instances
import asyncio

_job_queue: Optional[JobQueue] = None


def get_job_queue() -> JobQueue:
    """Get or create job queue"""
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue()
    return _job_queue
