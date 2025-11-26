"""File discovery, naming rules, and path handling."""

from typing import List
import os
from pathlib import Path


def scan_input_videos(root: str) -> List[str]:
    """Scan for input video files under the given root directory.

    The golden anchor's scanning rules (extensions, recursion, etc.) will be
    ported here without behavioral changes.
    """
    # TODO: Implement according to pubg_hevc_gui.py
    return []


def build_output_filename(input_path: str) -> str:
    """Construct the output filename according to the canonical rules.

    Example: PUBG_YYYY-MM-DD_HH-MM-SS_HEVC_P7.mp4
    The exact behavior must be cloned from the golden anchor.
    """
    # TODO: Implement according to pubg_hevc_gui.py
    base = Path(input_path).stem
    return base + "_encoded.mp4"

