"""Widget representing overall progress / telemetry."""

try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover
    QtWidgets = None  # type: ignore


class ProgressTile(QtWidgets.QWidget):  # type: ignore
    def __init__(self, parent=None):
        super(ProgressTile, self).__init__(parent)
        # TODO: Implement total ETA, GPU temperature, etc.

