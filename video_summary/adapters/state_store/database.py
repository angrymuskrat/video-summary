"""Concrete implementation of pipeline state persistence for the video summary pipeline."""


from __future__ import annotations

from video_summary.domain.models import PipelineState


class DatabaseStateStore:
    """State store implementation for database state."""
    def exists(self) -> bool:
        """Exists.
        
        Returns:
            bool: Result produced by exists.
        """
        raise NotImplementedError(
            "DatabaseStateStore is a contract placeholder. "
            "Add DB-backed state persistence here without changing the orchestrator."
        )

    def load(self) -> PipelineState:
        """Load the requested pipeline data.
        
        Returns:
            PipelineState: Result produced by load.
        """
        raise NotImplementedError(
            "DatabaseStateStore is a contract placeholder. "
            "Add DB-backed state persistence here without changing the orchestrator."
        )

    def save(self, state: PipelineState) -> None:
        """Save the requested pipeline data.
        
        Args:
            state (PipelineState): Value for state.
        """
        raise NotImplementedError(
            "DatabaseStateStore is a contract placeholder. "
            "Add DB-backed state persistence here without changing the orchestrator."
        )
