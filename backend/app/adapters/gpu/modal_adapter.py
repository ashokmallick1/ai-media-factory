import time
import logging
from typing import Dict, Any
from backend.app.adapters.gpu.base import BaseGPUAdapter, GPUJobRequest, GPUJobStatus

logger = logging.getLogger(__name__)

# Standard hourly pricing reference for GPU cost tracking
GPU_HOURLY_RATES = {
    "T4": 0.25,
    "A10G": 0.65,
    "L4": 0.70,
    "RTX4090": 0.74,
    "A100": 1.80,
    "H100": 3.95
}

class ModalGPUAdapter(BaseGPUAdapter):
    """
    Adapter for Modal / Serverless Python container execution.
    Features scale-to-zero, checkpointing, and per-second billing.
    """

    def __init__(self, api_token_id: str = None, api_token_secret: str = None):
        self.api_token_id = api_token_id
        self.api_token_secret = api_token_secret
        self._mock_jobs: Dict[str, Dict[str, Any]] = {}

    async def submit_job(self, request: GPUJobRequest) -> str:
        provider_job_id = f"modal-job-{request.job_id}"
        self._mock_jobs[provider_job_id] = {
            "request": request,
            "submitted_at": time.time(),
            "status": "running"
        }
        logger.info(f"Modal job {provider_job_id} submitted for task: {request.task_name} on {request.gpu_type}")
        return provider_job_id

    async def get_job_status(self, provider_job_id: str) -> GPUJobStatus:
        job = self._mock_jobs.get(provider_job_id)
        if not job:
            return GPUJobStatus(job_id=provider_job_id, status="failed", error_message="Job not found")

        elapsed = time.time() - job["submitted_at"]
        hourly_rate = GPU_HOURLY_RATES.get(job["request"].gpu_type, 0.65)
        cost = round((elapsed / 3600.0) * hourly_rate, 5)

        # Simulation completes within 2 seconds
        if elapsed >= 1.5:
            job["status"] = "completed"
            return GPUJobStatus(
                job_id=job["request"].job_id,
                status="completed",
                execution_time_seconds=round(elapsed, 2),
                cost_usd=cost,
                logs=f"[Modal] Completed {job['request'].task_name} on {job['request'].gpu_type}",
                output_data={"status": "success", "task": job["request"].task_name}
            )

        return GPUJobStatus(
            job_id=job["request"].job_id,
            status="running",
            execution_time_seconds=round(elapsed, 2),
            cost_usd=cost,
            logs="[Modal] Execution in progress..."
        )

    async def cancel_job(self, provider_job_id: str) -> bool:
        if provider_job_id in self._mock_jobs:
            self._mock_jobs[provider_job_id]["status"] = "canceled"
            return True
        return False
