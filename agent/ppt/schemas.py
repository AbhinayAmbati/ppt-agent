"""
PPT schemas for generation requests and responses
"""

from pydantic import BaseModel, Field
from datetime import datetime


class PromptRequest(BaseModel):
    """Request to generate PPT from prompt"""
    prompt: str = Field(..., min_length=10, max_length=1000, description="User prompt for PPT generation")


class PPTGenerationResponse(BaseModel):
    """Response from PPT generation"""
    job_id: str = Field(..., description="Unique job ID for tracking")
    status: str = Field(..., description="Job status: PENDING, RUNNING, COMPLETED, FAILED")
    message: str = Field(..., description="Status message")
    progress: int = Field(0, description="Progress percentage (0-100)")


class JobStatusResponse(BaseModel):
    """Response with job status info"""
    job_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    progress: int  # 0-100
    prompt: str
    result: dict | None

class DownloadResponse(BaseModel):
    """Response for file download"""
    file_name: str
    file_path: str
    download_url: str
