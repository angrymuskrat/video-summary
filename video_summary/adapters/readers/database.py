"""Concrete implementation of input reading for the video summary pipeline."""


from __future__ import annotations

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource


class DatabaseInputReader:
    """Input reader for database input."""
    def load(self, config: PipelineConfig) -> InputSource:
        """Load the requested pipeline data.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            InputSource: Result produced by load.
        """
        raise NotImplementedError(
            "DatabaseInputReader is a contract placeholder. "
            "Add a DB-backed lookup here without changing the orchestrator."
        )
