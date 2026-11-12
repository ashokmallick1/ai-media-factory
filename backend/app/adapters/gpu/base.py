from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class GPUJobRequest(BaseModel):
    job_id: str
    task_name: str # 'maya3_tts', 'whisper_asr', 'wan2_video', 'blender_render'
    image_uri: str = "nvidia/cuda:12.8.0-runtime-ubuntu22.04"
    gpu_type: str = "T4" # 'T4', 'A10G', 'L4', 'RTX4090', 'A100'
    gpu_count: int = 1
    timeout_seconds: int = 300
    env_vars: Dict[str, str] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)

class GPUJobStatus(BaseModel):
    job_id: str
    status: str # 'queued', 'running', 'completed', 'failed'
    execution_time_seconds: float = 0.0
    cost_usd: float = 0.0
    logs: str = ""
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

class BaseGPUAdapter(ABC):
    @abstractmethod
    async def submit_job(self, request: GPUJobRequest) -> str:
        """Submits a GPU task and returns provider job ID."""
        pass

    @abstractmethod
    async def get_job_status(self, provider_job_id: str) -> GPUJobStatus:
        """Polls or inspects the live status of the job."""
        pass

    @abstractmethod
    async def cancel_job(self, provider_job_id: str) -> bool:
        """Terminates a running GPU job."""
        pass
