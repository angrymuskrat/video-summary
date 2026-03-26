from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource


class InputReader(Protocol):
    def load(self, config: PipelineConfig) -> InputSource:
        ...
