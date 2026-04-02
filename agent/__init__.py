"""
Auto-PPT Agent - AI-powered presentation generation system
Core package initialization
"""

from agent_engine import init_agent, agent_engine
from mcp_client import mcp_client
from models import init_db

__version__ = "1.0.0"
__author__ = "Auto-PPT Team"

__all__ = [
    "init_agent",
    "agent_engine",
    "mcp_client",
    "init_db"
]
