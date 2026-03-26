from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import AlignmentResult, SpeakerTurn, WordToken


class AlignmentEngine(Protocol):
    def align(
        self,
        words: list[WordToken],
        turns: list[SpeakerTurn],
        config: PipelineConfig,
    ) -> AlignmentResult:
        ...
