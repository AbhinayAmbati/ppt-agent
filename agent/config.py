"""
Configuration Module
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server
    HOST: str
    PORT: int
    DEBUG: bool

    # Database
    DATABASE_URL: str

    # JWT & Security
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ALGORITHM: str = "HS256" # For compatibility with old code if needed
    ACCESS_TOKEN_EXPIRE_HOURS: int

    # HuggingFace
    HF_TOKEN: str
    LLM_MODEL: str
    DEVICE: str

    # MCP
    MCP_SERVERS_PATH: str = "mcp/servers"

    # Agent Config
    OUTPUT_DIR: str
    RATE_LIMIT_PER_HOUR: int
    MAX_CONCURRENT_JOBS: int
    JOB_TIMEOUT_SECONDS: int
    MCP_TOOL_TIMEOUT: int
    
    # CORS
    CORS_ORIGINS: str

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignore extra fields from .env

@lru_cache()
def get_settings():
    settings = Settings()
    settings.ALGORITHM = settings.JWT_ALGORITHM # map JWT_ALGORITHM config to ALGORITHM used in auth 
    return settings
