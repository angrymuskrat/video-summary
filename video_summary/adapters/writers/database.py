"""Concrete implementation of artifact writing for the video summary pipeline."""


from __future__ import annotations

from pathlib import Path
from typing import Any

from video_summary.domain.models import ArtifactRecord


class DatabaseArtifactWriter:
    """Artifact writer for database artifact."""
    def ensure_directories(self) -> None:
        """Ensure directories."""
        return None

    def frames_dir(self) -> Path:
        """Frames dir.
        
        Returns:
            Path: Result produced by frames dir.
        """
        raise NotImplementedError("DB-backed frame storage is not implemented yet.")

    def write_text(self, name: str, text: str) -> ArtifactRecord:
        """Write text.
        
        Args:
            name (str): Value for name.
            text (str): Value for text.
        
        Returns:
            ArtifactRecord: Result produced by write text.
        """
        raise NotImplementedError(
            "DatabaseArtifactWriter is a contract placeholder. "
            "Implement DB persistence here without changing the orchestrator."
        )

    def write_json(self, name: str, payload: Any) -> ArtifactRecord:
        """Write json.
        
        Args:
            name (str): Value for name.
            payload (Any): Value for payload.
        
        Returns:
            ArtifactRecord: Result produced by write json.
        """
        raise NotImplementedError(
            "DatabaseArtifactWriter is a contract placeholder. "
            "Implement DB persistence here without changing the orchestrator."
        )

    def register_file(self, name: str, path: Path, kind: str) -> ArtifactRecord:
        """Register file.
        
        Args:
            name (str): Value for name.
            path (Path): Filesystem path for the target resource.
            kind (str): Value for kind.
        
        Returns:
            ArtifactRecord: Result produced by register file.
        """
        raise NotImplementedError(
            "DatabaseArtifactWriter is a contract placeholder. "
            "Implement DB persistence here without changing the orchestrator."
        )
