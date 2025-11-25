# gui_settings.py
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
)

from config import Config


class SettingsDialog(QDialog):
    def __init__(self, parent, cfg: Config):
        super().__init__(parent)
        self.cfg = cfg

        self.setWindowTitle("FFmpeg Settings")
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        label = QLabel(
            "Edit the FFmpeg encoding template.\n"
            "Lines are split into arguments. Empty lines and lines starting with # are ignored.\n"
            "The program will run:\n"
            "  ffmpeg -y -i <input>  [template args]  -progress pipe:1 -nostats -loglevel error <output>\n"
        )
        layout.addWidget(label)

        self.text = QTextEdit()
        self.text.setPlainText(self.cfg.ffmpeg_template)
        layout.addWidget(self.text, stretch=1)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

    def get_template(self) -> str:
        return self.text.toPlainText()
