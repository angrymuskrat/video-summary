from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, SummaryResult, Utterance


class Summarizer(Protocol):
    def summarize(
        self,
        utterances: list[Utterance],
        slides: list[SceneSegment],
        config: PipelineConfig,
    ) -> SummaryResult:
        ...
