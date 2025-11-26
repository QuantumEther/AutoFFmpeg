import os
import subprocess
from typing import List, Tuple

from .model import JobModel, JobStatus
from .settings import load_settings


def build_output_name(input_filename: str) -> str:
    name, _ = os.path.splitext(input_filename)
    parts = name.split()

    if len(parts) < 2:
        return "PUBG_%s_HEVC_P7.mp4" % name.replace(" ", "_")

    date_part = parts[-2]
    time_part = parts[-1]
    new_name = "PUBG_%s_%s_HEVC_P7.mp4" % (date_part, time_part)
    return new_name


def probe_duration(ffprobe_path: str, file_path: str) -> float:
    try:
        cmd = [
            ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return float(output.strip())
    except Exception:
        return 0.0


def scan_videos(folder_path: str) -> Tuple[List[JobModel], str, str]:
    settings = load_settings()
    ffprobe_path = settings.get("ffprobe_path", "ffprobe")

    out_dir = os.path.join(folder_path, "HEVC_P7_Converted")
    os.makedirs(out_dir, exist_ok=True)

    mp4_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")]
    mp4_files.sort()

    jobs: List[JobModel] = []

    for idx, fname in enumerate(mp4_files):
        input_path = os.path.join(folder_path, fname)
        output_name = build_output_name(fname)
        output_path = os.path.join(out_dir, output_name)

        duration = probe_duration(ffprobe_path, input_path)

        if os.path.exists(output_path):
            status = JobStatus.SKIPPED_EXISTS.value
            progress = 1.0
        else:
            status = JobStatus.PENDING.value
            progress = 0.0

        job = JobModel(
            index=idx,
            input_path=input_path,
            output_path=output_path,
            duration=duration,
            status=status,
            progress=progress,
        )
        jobs.append(job)

    log_path = os.path.join(folder_path, "encoding_log.txt")

    return jobs, out_dir, log_path