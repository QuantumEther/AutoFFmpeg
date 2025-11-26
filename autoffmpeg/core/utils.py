"""Utility helpers for AutoFFmpeg."""

import subprocess
from typing import List, Tuple, Optional


def run_subprocess(command: List[str]) -> Tuple[int, str, str]:
    """Run a subprocess and capture stdout/stderr.

    This will later be aligned with the golden anchor's safe process execution
    (e.g. ffprobe, nvidia-smi).
    """
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


def get_gpu_temperature() -> Optional[float]:
    """Query the GPU temperature using nvidia-smi.

    Placeholder to be replaced with the exact logic from pubg_hevc_gui.py.
    """
    # TODO: Port exact GPU telemetry behavior.
    return None

