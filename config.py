# config.py
import os
import json
from dataclasses import dataclass, asdict
from typing import Optional

CONFIG_FILENAME = ".pubg_encoder_config.json"


def get_config_path():
    home = os.path.expanduser("~")
    return os.path.join(home, CONFIG_FILENAME)


DEFAULT_FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"


DEFAULT_FFMPEG_TEMPLATE = """\
-c:v hevc_nvenc
-preset p7
-profile:v main
-rc vbr
-cq 23
-g 10
-keyint_min 10
-rc-lookahead 20
-spatial-aq 1
-aq-strength 15
-temporal-aq 1
-c:a copy
"""


@dataclass
class Config:
    ffmpeg_path: str = DEFAULT_FFMPEG_PATH
    ffprobe_path: Optional[str] = None
    max_parallel_jobs: int = 3
    ffmpeg_template: str = DEFAULT_FFMPEG_TEMPLATE

    def ensure_paths(self):
        if not self.ffprobe_path:
            folder = os.path.dirname(self.ffmpeg_path)
            self.ffprobe_path = os.path.join(folder, "ffprobe.exe")


def load_config() -> Config:
    path = get_config_path()
    if not os.path.exists(path):
        cfg = Config()
        cfg.ensure_paths()
        return cfg

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = Config(
            ffmpeg_path=data.get("ffmpeg_path", DEFAULT_FFMPEG_PATH),
            ffprobe_path=data.get("ffprobe_path"),
            max_parallel_jobs=int(data.get("max_parallel_jobs", 3)),
            ffmpeg_template=data.get("ffmpeg_template", DEFAULT_FFMPEG_TEMPLATE),
        )
        cfg.ensure_paths()
        return cfg
    except Exception:
        cfg = Config()
        cfg.ensure_paths()
        return cfg


def save_config(cfg: Config):
    path = get_config_path()
    data = asdict(cfg)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        # If save fails, we just ignore; GUI will still run with current cfg
        pass
