"""Protocol definitions for alignment components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import AlignmentResult, SpeakerTurn, WordToken


class AlignmentEngine(Protocol):
    """Engine for alignment."""
    def align(
        self,
        words: list[WordToken],
        turns: list[SpeakerTurn],
        config: PipelineConfig,
    ) -> AlignmentResult:
        """Align the requested pipeline data.
        
        Args:
            words (list[WordToken]): Value for words.
            turns (list[SpeakerTurn]): Value for turns.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            AlignmentResult: Result produced by align.
        """
        ...
