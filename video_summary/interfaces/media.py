from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource, PreparedMedia


class MediaPreparator(Protocol):
    def prepare(self, source: InputSource, config: PipelineConfig) -> PreparedMedia:
        ...
