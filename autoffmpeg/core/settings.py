<<<<<<< ours
"""Settings handling for AutoFFmpeg.

Settings are stored in a JSON file in the project folder. This includes the
ffmpeg command template and any user preferences.
"""

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_SETTINGS = {
    "ffmpeg_template": "ffmpeg -y -i {input} {output}",
    "max_parallel_jobs": 3,
}


def get_settings_path() -> Path:
    return Path("settings.json").resolve()
=======
import json
from pathlib import Path
from typing import Dict, Any

DEFAULT_FFMPEG_PATH = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
DEFAULT_FFPROBE_PATH = str(Path(DEFAULT_FFMPEG_PATH).parent / "ffprobe.exe")
DEFAULT_TEMPLATE = "ffmpeg -y -i {input} {output}"
DEFAULT_MAX_PARALLEL_JOBS = 3


def get_settings_path() -> Path:
    return Path(__file__).resolve().parents[2] / "settings.json"


def _default_settings() -> Dict[str, Any]:
    return {
        "ffmpeg_path": DEFAULT_FFMPEG_PATH,
        "ffprobe_path": DEFAULT_FFPROBE_PATH,
        "ffmpeg_template": DEFAULT_TEMPLATE,
        "max_parallel_jobs": DEFAULT_MAX_PARALLEL_JOBS,
    }
>>>>>>> theirs


def load_settings() -> Dict[str, Any]:
    path = get_settings_path()
<<<<<<< ours
    if not path.exists():
        return DEFAULT_SETTINGS.copy()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_settings(data: Dict[str, Any]) -> None:
    path = get_settings_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

=======
    defaults = _default_settings()
    if not path.exists():
        save_settings(defaults)
        return defaults

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        save_settings(defaults)
        return defaults

    settings = {
        "ffmpeg_path": data.get("ffmpeg_path", DEFAULT_FFMPEG_PATH),
        "ffprobe_path": data.get("ffprobe_path", DEFAULT_FFPROBE_PATH),
        "ffmpeg_template": data.get("ffmpeg_template", DEFAULT_TEMPLATE),
        "max_parallel_jobs": int(data.get("max_parallel_jobs", DEFAULT_MAX_PARALLEL_JOBS)),
    }

    if not settings.get("ffprobe_path"):
        settings["ffprobe_path"] = str(Path(settings["ffmpeg_path"]).parent / "ffprobe.exe")

    save_settings(settings)
    return settings


def save_settings(settings: Dict[str, Any]) -> None:
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
>>>>>>> theirs
