"""Concrete implementation of input reading for the video summary pipeline."""


from __future__ import annotations

from dataclasses import dataclass

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource


@dataclass(frozen=True)
class DatabaseInputRecord:
    """Persisted input source metadata for a job-backed pipeline run."""

    video_path: str
    audio_path: str | None = None
    title: str | None = None


class DatabaseInputReader:
    """Input reader for database input."""
    def __init__(self, job_store: object, job_id: str) -> None:
        """Initialize the database input reader."""
        self._job_store = job_store
        self._job_id = job_id

    def load(self, config: PipelineConfig) -> InputSource:
        """Load the requested pipeline data.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            InputSource: Result produced by load.
        """
        record = self._job_store.get_job_input_record(self._job_id)
        return InputSource(
            video_path=record.video_path,
            audio_path=record.audio_path,
            title=record.title or config.input_path.stem,
        )
