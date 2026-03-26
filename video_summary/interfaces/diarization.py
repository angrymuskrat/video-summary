from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import SpeakerTurn


class DiarizationEngine(Protocol):
    def diarize(self, audio_path: str, config: PipelineConfig) -> list[SpeakerTurn]:
        ...
