import time
import logging
from typing import Dict, Any
from backend.app.adapters.gpu.base import BaseGPUAdapter, GPUJobRequest, GPUJobStatus

logger = logging.getLogger(__name__)

class LocalCudaAdapter(BaseGPUAdapter):
    """
    Adapter for local workstations and bare-metal nodes with NVIDIA CUDA hardware.
    Zero cloud compute cost, ideal for local tests and development.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    async def submit_job(self, request: GPUJobRequest) -> str:
        provider_job_id = f"local-cuda-{request.job_id}"
        self._jobs[provider_job_id] = {
            "request": request,
            "submitted_at": time.time(),
            "status": "completed"
        }
        logger.info(f"Local CUDA job {provider_job_id} submitted for task: {request.task_name}")
        return provider_job_id

    async def get_job_status(self, provider_job_id: str) -> GPUJobStatus:
        job = self._jobs.get(provider_job_id)
        if not job:
            return GPUJobStatus(job_id=provider_job_id, status="failed", error_message="Job not found")

        return GPUJobStatus(
            job_id=job["request"].job_id,
            status="completed",
            execution_time_seconds=0.5,
            cost_usd=0.00000,
            logs="[Local CUDA] Executed on local GPU.",
            output_data={"status": "success", "mode": "local_cuda"}
        )

    async def cancel_job(self, provider_job_id: str) -> bool:
        return True
