"""Animation metadata contains no GUI widgets or image I/O."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Animation:
    paths: tuple[Path, ...]
    interval_ms: int

    def __post_init__(self):
        if not self.paths or type(self.interval_ms) is not int or self.interval_ms <= 0:
            raise ValueError("Animation needs frames and a positive interval")
