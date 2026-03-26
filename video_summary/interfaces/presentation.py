"""Protocol definitions for presentation components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, SceneSegment


class PresentationGenerator(Protocol):
    """Generator for presentation."""
    def generate(self, slides: list[SceneSegment], title: str, config: PipelineConfig) -> list[ArtifactRecord]:
        """Generate the requested pipeline data.
        
        Args:
            slides (list[SceneSegment]): Value for slides.
            title (str): Value for title.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            list[ArtifactRecord]: Result produced by generate.
        """
        ...
