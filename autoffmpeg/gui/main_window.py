"""PyQt6 main window for AutoFFmpeg.

This module will eventually replace the Tkinter UI logic in the golden anchor.
"""

from typing import Optional

try:
    from PyQt6 import QtWidgets, QtCore
except ImportError:  # pragma: no cover
    QtWidgets = None  # type: ignore
    QtCore = None  # type: ignore


class MainWindow(QtWidgets.QMainWindow):  # type: ignore
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):  # type: ignore
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("AutoFFmpeg")
        self._setup_ui()

    def _setup_ui(self) -> None:
        # TODO: Implement full layout (queue, log, controls, telemetry)
        central = QtWidgets.QWidget(self)  # type: ignore
        layout = QtWidgets.QVBoxLayout(central)  # type: ignore
        layout.addWidget(QtWidgets.QLabel("AutoFFmpeg GUI skeleton"))  # type: ignore
        self.setCentralWidget(central)

