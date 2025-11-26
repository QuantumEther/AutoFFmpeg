"""Widget representing a single job entry in the queue."""

try:
    from PyQt6 import QtWidgets
except ImportError:  # pragma: no cover
    QtWidgets = None  # type: ignore


class JobTile(QtWidgets.QWidget):  # type: ignore
    def __init__(self, parent=None):
        super(JobTile, self).__init__(parent)
        # TODO: Implement job display (filename, status, ETA, progress)

