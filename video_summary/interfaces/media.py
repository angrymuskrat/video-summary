"""Protocol definitions for media components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource, PreparedMedia


class MediaPreparator(Protocol):
    """Media preparator."""
    def prepare(self, source: InputSource, config: PipelineConfig) -> PreparedMedia:
        """Prepare the requested pipeline data.
        
        Args:
            source (InputSource): Value for source.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            PreparedMedia: Result produced by prepare.
        """
        ...
