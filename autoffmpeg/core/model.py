"""In-memory model for jobs and queue state."""

from typing import List, Optional


class JobStatus(object):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobModel(object):
    """Represents a job in the queue."""

    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.status = JobStatus.PENDING
        self.progress = 0.0
        self.eta_seconds = None  # type: Optional[float]
        self.log_lines = []  # type: List[str]
        self.error_message = None  # type: Optional[str]


class QueueModel(object):
    """Represents the global job queue state."""

    def __init__(self):
        self.jobs = []  # type: List[JobModel]

    def add_job(self, job: JobModel) -> None:
        self.jobs.append(job)

