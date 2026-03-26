"""Protocol definitions for rendering components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, PreparedMedia


class VideoRenderer(Protocol):
    """Video renderer."""
    def render(self, prepared_media: PreparedMedia, config: PipelineConfig) -> list[ArtifactRecord]:
        """Render the requested pipeline data.
        
        Args:
            prepared_media (PreparedMedia): Value for prepared media.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            list[ArtifactRecord]: Result produced by render.
        """
        ...
