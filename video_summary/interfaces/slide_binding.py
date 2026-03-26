from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import PreparedMedia, SceneAnalysis, SceneSegment, Utterance


class SlideBinder(Protocol):
    def bind(
        self,
        scene_analysis: SceneAnalysis,
        utterances: list[Utterance],
        prepared_media: PreparedMedia,
        config: PipelineConfig,
    ) -> list[SceneSegment]:
        ...
