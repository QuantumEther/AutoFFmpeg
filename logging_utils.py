# logging_utils.py
import os
from datetime import datetime


def get_log_path(folder_path: str) -> str:
    return os.path.join(folder_path, "encoding_log.txt")


def append_log(folder_path: str, text: str):
    log_path = get_log_path(folder_path)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            ts = datetime.now().isoformat(timespec="seconds")
            f.write("[%s] %s" % (ts, text))
            if not text.endswith("\n"):
                f.write("\n")
    except Exception:
        pass
