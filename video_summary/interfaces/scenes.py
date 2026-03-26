"""Protocol definitions for scenes components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import MediaMetadata, SceneAnalysis


class SceneDetector(Protocol):
    """Scene detector."""
    def detect(self, video_path: str, metadata: MediaMetadata, config: PipelineConfig) -> SceneAnalysis:
        """Detect the requested pipeline data.
        
        Args:
            video_path (str): Filesystem path for video.
            metadata (MediaMetadata): Value for metadata.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            SceneAnalysis: Result produced by detect.
        """
        ...
