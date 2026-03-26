"""Protocol definitions for slide binding components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import PreparedMedia, SceneAnalysis, SceneSegment, Utterance


class SlideBinder(Protocol):
    """Slide binder."""
    def bind(
        self,
        scene_analysis: SceneAnalysis,
        utterances: list[Utterance],
        prepared_media: PreparedMedia,
        config: PipelineConfig,
    ) -> list[SceneSegment]:
        """Bind the requested pipeline data.
        
        Args:
            scene_analysis (SceneAnalysis): Value for scene analysis.
            utterances (list[Utterance]): Value for utterances.
            prepared_media (PreparedMedia): Value for prepared media.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            list[SceneSegment]: Result produced by bind.
        """
        ...
