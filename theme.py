# theme.py
from PyQt6.QtWidgets import QApplication

DARK_QSS = """
QWidget {
    background-color: #1e1e1e;
    color: #dddddd;
}

QTableWidget {
    gridline-color: #333333;
    background-color: #252525;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #dddddd;
    padding: 4px;
    border: 1px solid #444444;
}

QProgressBar {
    border: 1px solid #444;
    background-color: #333;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #00aaff;
}

QPushButton {
    background-color: #333;
    color: #eee;
    border: 1px solid #555;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #444;
}

QPushButton:pressed {
    background-color: #555;
}

QLineEdit, QTextEdit {
    background-color: #2a2a2a;
    color: #f0f0f0;
    border: 1px solid #555;
}

QGroupBox {
    border: 1px solid #444;
    margin-top: 6px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
}
"""


def apply_dark_theme(app: QApplication):
    app.setStyleSheet(DARK_QSS)
