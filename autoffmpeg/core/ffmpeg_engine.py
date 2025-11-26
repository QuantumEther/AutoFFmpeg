import os
import subprocess
import time
from typing import Callable

from .model import JobModel
from .settings import load_settings

settings = load_settings()
ffmpeg_path = settings.get("ffmpeg_path") or r"C:\\ffmpeg\\bin\\ffmpeg.exe"

ProgressCallback = Callable[[JobModel, float, float], None]


def build_ffmpeg_command(job: JobModel, ffmpeg_path: str) -> list:
    """
    Return the exact NVENC command from the golden anchor EncoderWorker.run(),
    expressed as a list of arguments.
    """
    return [
        ffmpeg_path,
        "-y",
        "-i",
        job.input_path,
        "-c:v",
        "hevc_nvenc",
        "-preset",
        "p7",
        "-profile:v",
        "main",
        "-rc",
        "vbr",
        "-cq",
        "23",
        "-g",
        "10",
        "-keyint_min",
        "10",
        "-rc-lookahead",
        "20",
        "-spatial-aq",
        "1",
        "-aq-strength",
        "15",
        "-temporal-aq",
        "1",
        "-c:a",
        "copy",
        "-progress",
        "pipe:1",
        "-nostats",
        "-loglevel",
        "error",
        job.output_path,
    ]


def run_ffmpeg_job(job: JobModel, on_progress: ProgressCallback) -> bool:
    """
    Run ffmpeg synchronously for the given job.

    Behavior must exactly reproduce EncoderWorker.run() from pubg_hevc_gui.py.
    """
    job.start_time = time.time()

    cmd = build_ffmpeg_command(job, ffmpeg_path)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
    except Exception:
        return False

    duration_sec = job.duration if getattr(job, "duration", 0) > 0 else None

    if process.stdout is not None:
        for line in process.stdout:
            line = line.strip()
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=", 1)[1])
                    position_sec = ms / 1_000_000.0
                    job.last_position_sec = position_sec
                    if duration_sec and duration_sec > 0:
                        progress = min(position_sec / duration_sec, 1.0)
                    else:
                        progress = 0.0
                    job.progress = progress
                    on_progress(job, progress, position_sec)
                except ValueError:
                    continue

    process.wait()
    success = process.returncode == 0 and os.path.exists(job.output_path)

    if success:
        job.progress = 1.0
        on_progress(job, 1.0, getattr(job, "duration", 0.0))

    return success
