"""Settings dialog for editing ffmpeg template and app options."""

from typing import Optional

try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover
    QtWidgets = None  # type: ignore


class SettingsWindow(QtWidgets.QDialog):  # type: ignore
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):  # type: ignore
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Settings")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)  # type: ignore
        layout.addWidget(QtWidgets.QLabel("Settings skeleton"))  # type: ignore
        self.setLayout(layout)

