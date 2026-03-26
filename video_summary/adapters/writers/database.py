"""Concrete implementation of artifact writing for the video summary pipeline."""


from __future__ import annotations

from pathlib import Path
from typing import Any

from video_summary.config import PipelineConfig
from video_summary.adapters.writers.filesystem import FilesystemArtifactWriter
from video_summary.domain.models import ArtifactRecord


class DatabaseArtifactWriter:
    """Artifact writer for database artifact."""
    def __init__(self, config: PipelineConfig, job_store: object, job_id: str) -> None:
        """Initialize the database artifact writer."""
        self._filesystem = FilesystemArtifactWriter(config)
        self._job_store = job_store
        self._job_id = job_id

    def ensure_directories(self) -> None:
        """Ensure directories."""
        self._filesystem.ensure_directories()

    def frames_dir(self) -> Path:
        """Frames dir.
        
        Returns:
            Path: Result produced by frames dir.
        """
        return self._filesystem.frames_dir()

    def write_text(self, name: str, text: str) -> ArtifactRecord:
        """Write text.
        
        Args:
            name (str): Value for name.
            text (str): Value for text.
        
        Returns:
            ArtifactRecord: Result produced by write text.
        """
        record = self._filesystem.write_text(name, text)
        return self.register_file(name, Path(record.path), record.kind)

    def write_json(self, name: str, payload: Any) -> ArtifactRecord:
        """Write json.
        
        Args:
            name (str): Value for name.
            payload (Any): Value for payload.
        
        Returns:
            ArtifactRecord: Result produced by write json.
        """
        record = self._filesystem.write_json(name, payload)
        return self.register_file(name, Path(record.path), record.kind)

    def register_file(self, name: str, path: Path, kind: str) -> ArtifactRecord:
        """Register file.
        
        Args:
            name (str): Value for name.
            path (Path): Filesystem path for the target resource.
            kind (str): Value for kind.
        
        Returns:
            ArtifactRecord: Result produced by register file.
        """
        record = self._filesystem.register_file(name, path, kind)
        self._job_store.record_artifact(self._job_id, record.name, record.path, record.kind)
        return record
