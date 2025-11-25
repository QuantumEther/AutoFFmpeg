# workers.py
import os
import subprocess
import time
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from model import EncoderJob
from config import Config
from ffmpeg_template import parse_template_args


class EncoderWorker(QThread):
    progress_signal = pyqtSignal(int, float, float)  # job_index, progress, position_sec
    status_signal = pyqtSignal(int, str)            # job_index, status
    finished_signal = pyqtSignal(int, bool)         # job_index, success

    def __init__(self, job: EncoderJob, cfg: Config, parent=None):
        super().__init__(parent)
        self.job = job
        self.cfg = cfg

    def build_command(self) -> list:
        job = self.job
        args = parse_template_args(self.cfg.ffmpeg_template)

        cmd = [
            self.cfg.ffmpeg_path,
            "-y",
            "-i",
            job.input_path,
        ]
        cmd.extend(args)
        # Force progress & logging options (not user-editable, for stability)
        cmd.extend([
            "-progress", "pipe:1",
            "-nostats",
            "-loglevel", "error",
            job.output_path,
        ])
        return cmd

    def run(self):
        job = self.job
        self.status_signal.emit(job.index, "Encoding")
        job.start_time = time.time()

        cmd = self.build_command()

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )
        except Exception:
            self.status_signal.emit(job.index, "Failed to start")
            self.finished_signal.emit(job.index, False)
            return

        duration_sec = job.duration if job.duration > 0 else None
        position_sec = 0.0

        if process.stdout is not None:
            for line in process.stdout:
                line = line.strip()
                if line.startswith("out_time_ms="):
                    try:
                        ms = int(line.split("=", 1)[1])
                        position_sec = ms / 1_000_000.0
                        job.last_position_sec = position_sec
                        if duration_sec and duration_sec > 0:
                            progress = min(position_sec / duration_sec, 1.0)
                        else:
                            progress = 0.0
                        self.progress_signal.emit(job.index, progress, position_sec)
                    except ValueError:
                        pass

        process.wait()
        success = (process.returncode == 0 and os.path.exists(job.output_path))

        if success:
            self.progress_signal.emit(job.index, 1.0, job.duration)
            self.status_signal.emit(job.index, "Done")
        else:
            self.status_signal.emit(job.index, "Failed")

        self.finished_signal.emit(job.index, success)
