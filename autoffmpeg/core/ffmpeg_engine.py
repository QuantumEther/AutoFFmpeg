"""FFmpeg execution and process management.

This module will gradually absorb ffmpeg-related logic from golden_anchor/pubg_hevc_gui.py,
preserving behavior exactly while improving structure and testability.
"""

from typing import List, Dict, Optional


class FFmpegJob(object):
    """Represents a single ffmpeg encoding job."""

    def __init__(self, input_path: str, output_path: str, command: List[str]):
        self.input_path = input_path
        self.output_path = output_path
        self.command = command
        self.process = None
        self.returncode = None
        self.progress = 0.0
        self.eta_seconds = None  # type: Optional[float]


def build_ffmpeg_command(input_path: str, output_path: str, template: str) -> List[str]:
    """Build the ffmpeg command list from a template.

    This is a placeholder. The real implementation will be ported from the
    golden anchor while keeping the exact behavior and defaults.
    """
    # TODO: Implement using golden anchor logic.
    return ["ffmpeg", "-i", input_path, output_path]


def run_ffmpeg_job(job: FFmpegJob) -> int:
    """Run a single ffmpeg job synchronously.

    In the final architecture this will be driven from a worker thread.
    """
    # TODO: Port process execution, logging, and progress parsing from golden anchor.
    raise NotImplementedError("run_ffmpeg_job is not implemented yet.")

