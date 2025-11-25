# ffmpeg_template.py
import os
from typing import List


def build_output_name(input_filename: str) -> str:
    """
    Convert:
        PLAYERUNKNOWN'S BATTLEGROUNDS  2019-11-21 19-40-36.mp4
    to:
        PUBG_2019-11-21_19-40-36_HEVC_P7.mp4
    """
    name, _ = os.path.splitext(input_filename)
    parts = name.split()

    if len(parts) < 2:
        return "PUBG_%s_HEVC_P7.mp4" % name.replace(" ", "_")

    date_part = parts[-2]
    time_part = parts[-1]
    new_name = "PUBG_%s_%s_HEVC_P7.mp4" % (date_part, time_part)
    return new_name


def parse_template_args(template: str) -> List[str]:
    """
    Split ffmpeg template into argument list.
    Each non-empty line is split by whitespace.
    Lines starting with '#' are treated as comments and ignored.
    """
    args: List[str] = []
    for line in template.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        parts = line.split()
        args.extend(parts)
    return args
