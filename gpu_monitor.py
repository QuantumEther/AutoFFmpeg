# gpu_monitor.py
import subprocess


def get_gpu_temperature() -> str:
    """
    Query GPU temperature using nvidia-smi.
    Returns 'N/A' on failure.
    """
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        line = output.strip().splitlines()[0].strip()
        return "%s °C" % line
    except Exception:
        return "N/A"
