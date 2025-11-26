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


def load_settings() -> Dict[str, Any]:
    path = get_settings_path()
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

