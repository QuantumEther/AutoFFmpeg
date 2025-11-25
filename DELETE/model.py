# model.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EncoderJob:
    index: int
    input_path: str
    output_path: str
    duration: float = 0.0  # seconds
    status: str = "Pending"
    progress: float = 0.0  # 0..1
    start_time: Optional[float] = None
    last_position_sec: float = 0.0  # last encoded time in seconds
