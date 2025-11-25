# gui_main.py
import os
import time
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
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

from config import Config, save_config
from model import EncoderJob
from ffmpeg_template import build_output_name
from duration_probe import probe_duration
from gpu_monitor import get_gpu_temperature
from logging_utils import append_log
from workers import EncoderWorker
from gui_settings import SettingsDialog


def format_hms(seconds: float) -> str:
    if seconds is None or seconds <= 0:
        return "--:--"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return "%d:%02d:%02d" % (hours, minutes, secs)
    return "%02d:%02d" % (minutes, secs)


class MainWindow(QMainWindow):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg

        self.setWindowTitle("PUBG HEVC P7 Encoder — 3 Parallel Jobs (PyQt6)")
        self.resize(1000, 600)

        self.folder_path: Optional[str] = None
        self.jobs = []          # type: list[EncoderJob]
        self.workers = {}       # type: dict[int, EncoderWorker]
        self.active_jobs = 0

        self._build_ui()

        self.info_timer = QTimer(self)
        self.info_timer.timeout.connect(self.update_info_panel)
        self.info_timer.start(1000)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # Top controls
        top_layout = QHBoxLayout()
        self.folder_label = QLabel("Folder: (none selected)")
        btn_select = QPushButton("Select Folder...")
        btn_select.clicked.connect(self.select_folder)

        btn_settings = QPushButton("Settings")
        btn_settings.clicked.connect(self.open_settings)

        self.btn_start = QPushButton("Start Encoding")
        self.btn_start.clicked.connect(self.start_encoding)
        self.btn_start.setEnabled(False)

        top_layout.addWidget(self.folder_label, stretch=1)
        top_layout.addWidget(btn_select)
        top_layout.addWidget(btn_settings)
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

    # ---------- UI Actions ----------

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with PUBG MP4 Files")
        if not folder:
            return
        self.folder_path = folder
        self.folder_label.setText("Folder: %s" % folder)
        self.scan_folder()

    def scan_folder(self):
        self.jobs = []
        self.workers = {}
        self.active_jobs = 0
        self.table.setRowCount(0)

        if not self.folder_path:
            return

        out_dir = os.path.join(self.folder_path, "HEVC_P7_Converted")
        os.makedirs(out_dir, exist_ok=True)

        mp4_files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith(".mp4")
        ]

        if not mp4_files:
            QMessageBox.warning(self, "No files", "No .mp4 files found in this folder.")
            self.btn_start.setEnabled(False)
            return

        mp4_files.sort()
        for idx, fname in enumerate(mp4_files):
            input_path = os.path.join(self.folder_path, fname)
            output_name = build_output_name(fname)
            output_path = os.path.join(out_dir, output_name)

            duration = probe_duration(self.cfg.ffprobe_path, input_path)

            job = EncoderJob(
                index=idx,
                input_path=input_path,
                output_path=output_path,
                duration=duration,
            )

            if os.path.exists(output_path):
                job.status = "Skipped (exists)"
                job.progress = 1.0
            else:
                job.status = "Pending"
                job.progress = 0.0

            self.jobs.append(job)

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
        append_log(self.folder_path, "Scan completed. %d files found." % len(self.jobs))

    def start_encoding(self):
        if not self.jobs:
            return
        self.btn_start.setEnabled(False)
        append_log(self.folder_path, "Encoding started.")
        self.start_next_jobs()

    # ---------- Settings ----------

    def open_settings(self):
        dlg = SettingsDialog(self, self.cfg)
        if dlg.exec():
            self.cfg.ffmpeg_template = dlg.get_template()
            save_config(self.cfg)
            QMessageBox.information(self, "Settings saved", "FFmpeg template updated.")

    # ---------- Scheduling ----------

    def get_next_pending_job(self) -> Optional[EncoderJob]:
        for job in self.jobs:
            if job.status == "Pending":
                return job
        return None

    def start_next_jobs(self):
        while self.active_jobs < self.cfg.max_parallel_jobs:
            next_job = self.get_next_pending_job()
            if not next_job:
                break
            self.launch_job(next_job)

        if self.active_jobs == 0 and not self.get_next_pending_job():
            append_log(self.folder_path, "All encodes completed.")
            QMessageBox.information(self, "Done", "All encodes completed.")

    def launch_job(self, job: EncoderJob):
        job.status = "Encoding"
        row = job.index
        self.table.item(row, 1).setText(job.status)

        append_log(
            self.folder_path,
            "START: %s -> %s (duration=%.2fs)" % (job.input_path, job.output_path, job.duration),
        )

        worker = EncoderWorker(job, self.cfg)
        worker.progress_signal.connect(self.on_job_progress)
        worker.status_signal.connect(self.on_job_status)
        worker.finished_signal.connect(self.on_job_finished)
        self.workers[job.index] = worker

        self.active_jobs += 1
        worker.start()

    # ---------- Worker slots ----------

    def on_job_progress(self, job_index: int, progress: float, position_sec: float):
        job = self.jobs[job_index]
        job.progress = progress
        job.last_position_sec = position_sec

        row = job.index
        progress_bar = self.table.cellWidget(row, 2)
        if isinstance(progress_bar, QProgressBar):
            progress_bar.setValue(int(progress * 100))

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

        append_log(
            self.folder_path,
            "END: %s status=%s elapsed=%.1fs"
            % (job.input_path, "OK" if success else "FAIL", elapsed),
        )

        # Set ETA to 00:00 on finish
        eta_item = self.table.item(job.index, 3)
        if eta_item:
            eta_item.setText("00:00")

        self.start_next_jobs()

    # ---------- Info panel / ETA / GPU ----------

    def update_info_panel(self):
        # GPU temp
        gpu_temp = get_gpu_temperature()
        self.label_gpu.setText("GPU: %s" % gpu_temp)

        total_remaining = 0.0
        pending_count = 0
        encoding_count = 0
        done_count = 0

        now = time.time()

        for job in self.jobs:
            row = job.index
            eta_item = self.table.item(row, 3)

            if job.status == "Pending":
                pending_count += 1
                remaining = job.duration
                total_remaining += remaining
                if eta_item:
                    eta_item.setText(format_hms(job.duration))

            elif job.status == "Encoding":
                encoding_count += 1
                if job.start_time is not None and job.progress > 0.0:
                    elapsed = now - job.start_time
                    est_total = elapsed / job.progress
                    remaining = max(est_total - elapsed, 0.0)
                else:
                    remaining = job.duration
                total_remaining += remaining
                if eta_item:
                    eta_item.setText(format_hms(remaining))

            else:
                if job.status.startswith("Skipped") or job.status == "Done":
                    done_count += 1
                if eta_item and eta_item.text() in ("--:--", ""):
                    eta_item.setText("00:00")

        self.label_overall_eta.setText("Total ETA: %s" % format_hms(total_remaining))
        self.label_queue.setText(
            "Queue: %d pending, %d encoding, %d done"
            % (pending_count, encoding_count, done_count)
        )
