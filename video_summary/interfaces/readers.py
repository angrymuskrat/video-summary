"""Protocol definitions for readers components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource


class InputReader(Protocol):
    """Input reader for input."""
    def load(self, config: PipelineConfig) -> InputSource:
        """Load the requested pipeline data.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            InputSource: Result produced by load.
        """
        ...
