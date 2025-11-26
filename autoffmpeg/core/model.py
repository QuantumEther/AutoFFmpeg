<<<<<<< ours
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

=======
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class JobStatus(str, Enum):
    PENDING = "Pending"
    ENCODING = "Encoding"
    DONE = "Done"
    SKIPPED_EXISTS = "Skipped (exists)"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class JobModel:
    index: int
    input_path: str
    output_path: str
    duration: float
    status: str
    progress: float
    start_time: Optional[float] = None
    last_position_sec: float = 0.0
    eta_seconds: Optional[float] = None
    log_lines: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class QueueModel:
    jobs: List[JobModel] = field(default_factory=list)
>>>>>>> theirs
