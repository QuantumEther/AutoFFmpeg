# main.py
import sys

from PyQt6.QtWidgets import QApplication

from config import load_config
from theme import apply_dark_theme
from gui_main import MainWindow


def main():
    app = QApplication(sys.argv)

    cfg = load_config()
    win = MainWindow(cfg)
    apply_dark_theme(app)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
