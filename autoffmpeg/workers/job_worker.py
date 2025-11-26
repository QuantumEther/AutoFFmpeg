"""Worker thread / runnable for executing ffmpeg jobs."""

from typing import Optional

try:
    from PyQt6 import QtCore
except ImportError:  # pragma: no cover
    QtCore = None  # type: ignore


class JobWorker(QtCore.QObject):  # type: ignore
    # TODO: Define signals for progress, completion, logging, etc.
    def __init__(self, job_model, parent: Optional[QtCore.QObject] = None):  # type: ignore
        super(JobWorker, self).__init__(parent)
        self.job_model = job_model

    def run(self) -> None:
        """Main execution entry. To be moved into a QThread or QRunnable."""
        # TODO: Integrate with core.ffmpeg_engine
        raise NotImplementedError("JobWorker.run is not implemented yet.")

