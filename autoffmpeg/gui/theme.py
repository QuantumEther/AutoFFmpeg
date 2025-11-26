"""Dark theme handling for AutoFFmpeg GUI."""

from pathlib import Path


def load_dark_theme_qss() -> str:
    """Load the dark theme QSS from resources, if available."""
    qss_path = Path(__file__).resolve().parent.parent.parent / "resources" / "qss" / "dark.qss"
    if qss_path.exists():
        with qss_path.open("r", encoding="utf-8") as f:
            return f.read()
    return ""

