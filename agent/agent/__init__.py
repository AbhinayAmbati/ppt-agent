"""Agent module for LLM planning and presentation generation"""

from agent.llm_client import LLMClient, SlideSpec, PresentationPlan, get_llm_client
from agent.mcp_client import MCPClientPool, MCPClientConnection, get_mcp_pool, shutdown_mcp, ToolResult
from agent.executor import PPTExecutor, JobQueue, get_job_queue

__all__ = [
    "LLMClient",
    "SlideSpec",
    "PresentationPlan",
    "get_llm_client",
    "MCPClientPool",
    "MCPClientConnection",
    "get_mcp_pool",
    "shutdown_mcp",
    "ToolResult",
    "PPTExecutor",
    "JobQueue",
    "get_job_queue"
]
