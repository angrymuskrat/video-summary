"""Protocol definitions for state store components."""


from __future__ import annotations

from typing import Protocol

from video_summary.domain.models import PipelineState


class StateStore(Protocol):
    """State store implementation for state."""
    def exists(self) -> bool:
        """Exists.
        
        Returns:
            bool: Result produced by exists.
        """
        ...

    def load(self) -> PipelineState:
        """Load the requested pipeline data.
        
        Returns:
            PipelineState: Result produced by load.
        """
        ...

    def save(self, state: PipelineState) -> None:
        """Save the requested pipeline data.
        
        Args:
            state (PipelineState): Value for state.
        """
        ...
