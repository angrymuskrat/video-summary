"""Concrete implementation of pipeline state persistence for the video summary pipeline."""


from __future__ import annotations

import json

from video_summary.config import PipelineConfig
from video_summary.domain.models import PipelineState


class FilesystemStateStore:
    """State store implementation for filesystem state."""
    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the filesystem state store.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        """
        self._path = config.layout().state_path

    def exists(self) -> bool:
        """Exists.
        
        Returns:
            bool: Result produced by exists.
        """
        return self._path.exists()

    def load(self) -> PipelineState:
        """Load the requested pipeline data.
        
        Returns:
            PipelineState: Result produced by load.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f"State file '{self._path}' is missing. Run a full pipeline first or restart from 'prepare'."
            )
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return PipelineState.from_dict(data)

    def save(self, state: PipelineState) -> None:
        """Save the requested pipeline data.
        
        Args:
            state (PipelineState): Value for state.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
