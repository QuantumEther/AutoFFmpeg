import os
import sys
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QTimer,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QMessageBox,
    QHeaderView,
    QGroupBox,
)

# ===================== CONFIGURATION =====================

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # adjust if needed
FFPROBE_PATH = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe.exe")

MAX_PARALLEL_JOBS = 3
OUTPUT_SUBDIR = "HEVC_P7_Converted"
LOG_FILENAME = "encoding_log.txt"

# ========================================================


def format_hms(seconds: float) -> str:
    """Format seconds as H:MM:SS."""
    if seconds is None or seconds <= 0:
        return "--:--"
    seconds = int(seconds)
    return str(timedelta(seconds=seconds))


def build_output_name(input_filename: str) -> str:
    """
    Convert:
        PLAYERUNKNOWN'S BATTLEGROUNDS  2019-11-21 19-40-36.mp4
    to:
        PUBG_2019-11-21_19-40-36_HEVC_P7.mp4
    """
    name, _ = os.path.splitext(input_filename)
    parts = name.split()

    if len(parts) < 2:
        # Fallback
        return f"PUBG_{name}_HEVC_P7.mp4"

    date_part = parts[-2]
    time_part = parts[-1]
    new_name = f"PUBG_{date_part}_{time_part}_HEVC_P7.mp4"
    return new_name


def probe_duration(file_path: str) -> Optional[float]:
    """Use ffprobe to get duration in seconds."""
    try:
        cmd = [
            FFPROBE_PATH,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return float(output.strip())
    except Exception:
        return None


def get_gpu_temperature() -> str:
    """Query GPU temperature using nvidia-smi. Returns 'N/A' on failure."""
    try:
        output = subprocess.check_output(
            ["nvidia-smi",
             "--query-gpu=temperature.gpu",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        line = output.strip().splitlines()[0].strip()
        return f"{line} °C"
    except Exception:
        return "N/A"


class EncoderJob:
    def __init__(self, index: int, input_path: str, output_path: str, duration: Optional[float]):
        self.index = index
        self.input_path = input_path
        self.output_path = output_path
        self.duration = duration or 0.0
        self.status = "Pending"
        self.progress = 0.0  # 0..1
        self.start_time: Optional[float] = None
        self.last_position_sec: float = 0.0  # latest known encoded time


class EncoderWorker(QThread):
    progress_signal = pyqtSignal(int, float, float)  # job_index, progress, position_sec
    status_signal = pyqtSignal(int, str)             # job_index, status text
    finished_signal = pyqtSignal(int, bool)          # job_index, success bool

    def __init__(self, job: EncoderJob, ffmpeg_path: str, parent=None):
        super().__init__(parent)
        self.job = job
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        job = self.job
        self.status_signal.emit(job.index, "Encoding")
        job.start_time = time.time()

        # Build FFmpeg command with progress
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", job.input_path,
            "-c:v", "hevc_nvenc",
            "-preset", "p7",
            "-profile:v", "main",
            "-rc", "vbr",
            "-cq", "23",
            "-g", "10",
            "-keyint_min", "10",
            "-rc-lookahead", "20",
            "-spatial-aq", "1",
            "-aq-strength", "15",
            "-temporal-aq", "1",
            "-c:a", "copy",
            "-progress", "pipe:1",
            "-nostats",
            "-loglevel", "error",
            job.output_path,
        ]

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

        # Parse -progress key=value output
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PUBG HEVC P7 Encoder — 3 Parallel Jobs (PyQt6)")
        self.resize(900, 600)

        self.folder_path: Optional[str] = None
        self.jobs: list[EncoderJob] = []
        self.workers: dict[int, EncoderWorker] = {}
        self.active_jobs = 0
        self.log_file_path: Optional[str] = None

        self._build_ui()

        # Timer: GPU temperature + ETA updates
        self.info_timer = QTimer(self)
        self.info_timer.timeout.connect(self.update_info_panel)
        self.info_timer.start(1000)  # every second

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # Top controls
        top_layout = QHBoxLayout()
        self.folder_label = QLabel("Folder: (none selected)")
        btn_select = QPushButton("Select Folder...")
        btn_select.clicked.connect(self.select_folder)
        self.btn_start = QPushButton("Start Encoding")
        self.btn_start.clicked.connect(self.start_encoding)
        self.btn_start.setEnabled(False)

        top_layout.addWidget(self.folder_label, stretch=1)
        top_layout.addWidget(btn_select)
        top_layout.addWidget(self.btn_start)

        main_layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["File", "Status", "Progress", "ETA"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table, stretch=1)

        # Info panel
        info_box = QGroupBox("Status")
        info_layout = QHBoxLayout()
        info_box.setLayout(info_layout)

        self.label_gpu = QLabel("GPU: N/A")
        self.label_overall_eta = QLabel("Total ETA: --:--")
        self.label_queue = QLabel("Queue: 0 pending, 0 encoding, 0 done")

        info_layout.addWidget(self.label_gpu)
        info_layout.addWidget(self.label_overall_eta)
        info_layout.addWidget(self.label_queue)
        main_layout.addWidget(info_box)

    # ----------------- UI Actions -----------------

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with PUBG MP4 Files")
        if not folder:
            return
        self.folder_path = folder
        self.folder_label.setText(f"Folder: {folder}")
        self.scan_folder()

    def scan_folder(self):
        """Scan selected folder for .mp4 files and build job list."""
        self.jobs.clear()
        self.table.setRowCount(0)
        self.workers.clear()
        self.active_jobs = 0

        if not self.folder_path:
            return

        out_dir = os.path.join(self.folder_path, OUTPUT_SUBDIR)
        os.makedirs(out_dir, exist_ok=True)

        self.log_file_path = os.path.join(self.folder_path, LOG_FILENAME)

        mp4_files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith(".mp4")
        ]

        if not mp4_files:
            QMessageBox.warning(self, "No files", "No .mp4 files found in this folder.")
            self.btn_start.setEnabled(False)
            return

        # Probe durations (can take a bit)
        for idx, fname in enumerate(sorted(mp4_files)):
            input_path = os.path.join(self.folder_path, fname)
            output_name = build_output_name(fname)
            output_path = os.path.join(out_dir, output_name)

            duration = probe_duration(input_path)

            job = EncoderJob(index=idx, input_path=input_path, output_path=output_path, duration=duration)

            # Determine initial status
            if os.path.exists(output_path):
                job.status = "Skipped (exists)"
                job.progress = 1.0
            else:
                job.status = "Pending"
                job.progress = 0.0

            self.jobs.append(job)

            # Add row to table
            row = self.table.rowCount()
            self.table.insertRow(row)

            item_file = QTableWidgetItem(os.path.basename(input_path))
            item_file.setFlags(item_file.flags() & ~Qt.ItemFlag.ItemIsEditable)

            item_status = QTableWidgetItem(job.status)
            item_status.setFlags(item_status.flags() & ~Qt.ItemFlag.ItemIsEditable)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(job.progress * 100))

            item_eta = QTableWidgetItem("--:--")
            item_eta.setFlags(item_eta.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row, 0, item_file)
            self.table.setItem(row, 1, item_status)
            self.table.setCellWidget(row, 2, progress_bar)
            self.table.setItem(row, 3, item_eta)

        self.btn_start.setEnabled(True)
        self.append_log(f"[{datetime.now()}] Scan completed. {len(self.jobs)} files found.\n")

    def start_encoding(self):
        if not self.jobs:
            return
        self.btn_start.setEnabled(False)
        self.append_log(f"[{datetime.now()}] Encoding started.\n")
        self.start_next_jobs()

    # ----------------- Job Scheduling -----------------

    def start_next_jobs(self):
        """Start new jobs until we reach MAX_PARALLEL_JOBS or no pending jobs remain."""
        while self.active_jobs < MAX_PARALLEL_JOBS:
            next_job = self.get_next_pending_job()
            if not next_job:
                break
            self.launch_job(next_job)

        # If no active jobs and no pending, all done
        if self.active_jobs == 0 and not self.get_next_pending_job():
            self.append_log(f"[{datetime.now()}] All encodes completed.\n")
            QMessageBox.information(self, "Done", "All encodes completed.")

    def get_next_pending_job(self):# -> Optional(EncoderJob):
        for job in self.jobs:
            if job.status == "Pending":
                return job
        return None

    def launch_job(self, job: EncoderJob):
        job.status = "Encoding"
        row = job.index
        self.table.item(row, 1).setText(job.status)

        # Log start
        self.append_log(
            f"[{datetime.now()}] START: {job.input_path} "
            f"-> {job.output_path} (duration={job.duration:.2f}s)\n"
        )

        worker = EncoderWorker(job, FFMPEG_PATH)
        worker.progress_signal.connect(self.on_job_progress)
        worker.status_signal.connect(self.on_job_status)
        worker.finished_signal.connect(self.on_job_finished)
        self.workers[job.index] = worker

        self.active_jobs += 1
        job.start_time = time.time()
        worker.start()

    # ----------------- Slots from workers -----------------

    def on_job_progress(self, job_index: int, progress: float, position_sec: float):
        job = self.jobs[job_index]
        job.progress = progress
        job.last_position_sec = position_sec

        row = job.index
        progress_bar = self.table.cellWidget(row, 2)
        if isinstance(progress_bar, QProgressBar):
            progress_bar.setValue(int(progress * 100))

        # ETA per-file will be computed in update_info_panel()

    def on_job_status(self, job_index: int, status: str):
        job = self.jobs[job_index]
        job.status = status
        row = job.index
        self.table.item(row, 1).setText(status)

    def on_job_finished(self, job_index: int, success: bool):
        job = self.jobs[job_index]
        self.active_jobs = max(0, self.active_jobs - 1)

        elapsed = 0.0
        if job.start_time is not None:
            elapsed = time.time() - job.start_time

        self.append_log(
            f"[{datetime.now()}] END: {job.input_path} "
            f"status={'OK' if success else 'FAIL'} "
            f"elapsed={elapsed:.1f}s\n"
        )

        # Update per-file ETA cell to 0
        eta_item = self.table.item(job.index, 3)
        if eta_item:
            eta_item.setText("00:00")

        # Start next jobs if available
        self.start_next_jobs()

    # ----------------- Info / ETA / GPU panel -----------------

    def update_info_panel(self):
        # GPU temperature
        gpu_temp = get_gpu_temperature()
        self.label_gpu.setText(f"GPU: {gpu_temp}")

        # Per-file ETA + overall ETA + queue stats
        total_remaining = 0.0
        pending_count = 0
        encoding_count = 0
        done_count = 0

        now = time.time()

        for job in self.jobs:
            row = job.index
            item_eta = self.table.item(row, 3)

            if job.status == "Pending":
                pending_count += 1
                # approximate remaining as full duration
                remaining = job.duration
                total_remaining += remaining
                if item_eta:
                    item_eta.setText(format_hms(job.duration))
            elif job.status == "Encoding":
                encoding_count += 1
                # compute ETA based on last position and start_time
                if job.start_time is not None and job.progress > 0:
                    elapsed = now - job.start_time
                    est_total = elapsed / job.progress
                    remaining = max(est_total - elapsed, 0.0)
                else:
                    remaining = job.duration
                total_remaining += remaining
                if item_eta:
                    item_eta.setText(format_hms(remaining))
            else:
                if job.status.startswith("Skipped") or job.status == "Done":
                    done_count += 1
                if item_eta and item_eta.text() in ("--:--", ""):
                    item_eta.setText("00:00")

        self.label_overall_eta.setText(f"Total ETA: {format_hms(total_remaining)}")
        self.label_queue.setText(
            f"Queue: {pending_count} pending, {encoding_count} encoding, {done_count} done"
        )

    # ----------------- Logging -----------------

    def append_log(self, text: str):
        if not self.log_file_path:
            return
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
