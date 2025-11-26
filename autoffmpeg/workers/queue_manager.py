"""Queue manager responsible for scheduling and parallelism."""

from typing import Optional


class QueueManager(object):
    """Controls job submission and N-parallel execution."""

    def __init__(self, max_parallel_jobs: int = 3):
        self.max_parallel_jobs = max_parallel_jobs
        self._queue = []
        self._running = []

    def add_job(self, job_model) -> None:
        self._queue.append(job_model)

    def start_next_jobs(self) -> None:
        """Start jobs while there is capacity.

        The detailed behavior will be ported from the golden anchor.
        """
        # TODO: Implement scheduling logic
        pass

