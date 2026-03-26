"""Concrete implementation of pipeline state persistence for the video summary pipeline."""


from __future__ import annotations

import json

from video_summary.domain.models import PipelineState


class DatabaseStateStore:
    """State store implementation for database state."""
    def __init__(self, job_store: object, job_id: str) -> None:
        """Initialize the database state store."""
        self._job_store = job_store
        self._job_id = job_id

    def exists(self) -> bool:
        """Exists.
        
        Returns:
            bool: Result produced by exists.
        """
        return self._job_store.has_pipeline_state(self._job_id)

    def load(self) -> PipelineState:
        """Load the requested pipeline data.
        
        Returns:
            PipelineState: Result produced by load.
        """
        payload = self._job_store.load_pipeline_state(self._job_id)
        if payload is None:
            raise FileNotFoundError("Job state is missing in the database-backed state store.")
        if isinstance(payload, str):
            payload = json.loads(payload)
        return PipelineState.from_dict(payload)

    def save(self, state: PipelineState) -> None:
        """Save the requested pipeline data.
        
        Args:
            state (PipelineState): Value for state.
        """
        self._job_store.save_pipeline_state(self._job_id, state.to_dict(), state.start_from)

    def mark_step_started(self, step_name: str) -> None:
        """Persist the currently running pipeline step for status reporting."""
        self._job_store.mark_current_step(self._job_id, step_name)
