"""Protocol definitions for subtitles components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, MediaMetadata, Utterance


class SubtitleGenerator(Protocol):
    """Generator for subtitle."""
    def generate(
        self,
        subtitles: list[Utterance],
        metadata: MediaMetadata,
        config: PipelineConfig,
    ) -> list[ArtifactRecord]:
        """Generate the requested pipeline data.
        
        Args:
            subtitles (list[Utterance]): Value for subtitles.
            metadata (MediaMetadata): Value for metadata.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            list[ArtifactRecord]: Result produced by generate.
        """
        ...
