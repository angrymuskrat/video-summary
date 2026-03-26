"""Protocol definitions for summarization components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, SummaryResult, Utterance


class Summarizer(Protocol):
    """Summarizer."""
    def summarize(
        self,
        utterances: list[Utterance],
        slides: list[SceneSegment],
        config: PipelineConfig,
    ) -> SummaryResult:
        """Summarize the requested pipeline data.
        
        Args:
            utterances (list[Utterance]): Value for utterances.
            slides (list[SceneSegment]): Value for slides.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            SummaryResult: Result produced by summarize.
        """
        ...
