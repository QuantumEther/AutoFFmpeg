# duration_probe.py
import subprocess


def probe_duration(ffprobe_path: str, file_path: str) -> float:
    """
    Use ffprobe to get duration in seconds.
    Returns 0.0 on failure.
    """
    try:
        cmd = [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        output = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, text=True
        )
        return float(output.strip())
    except Exception:
        return 0.0
