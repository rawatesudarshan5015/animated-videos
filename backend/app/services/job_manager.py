from typing import Dict, Any, Optional
from datetime import datetime

class JobManager:
    """
    In-memory job tracker for the video processing pipeline.
    Stores job status, output path, and errors.
    """
    def __init__(self):
        # Format: { "job_id": { "status": "processing", "result": None, "error": None, "created_at": str } }
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, job_id: str) -> None:
        self.jobs[job_id] = {
            "status": "processing",
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat()
        }

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

    def mark_completed(self, job_id: str, result: dict) -> None:
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["result"] = result

    def mark_failed(self, job_id: str, error_msg: str) -> None:
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = error_msg

# Global singleton instance for the FastAPI application
job_manager = JobManager()
