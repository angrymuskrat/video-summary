"""Protocol definitions for writers components."""


from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from video_summary.domain.models import ArtifactRecord


class ArtifactWriter(Protocol):
    """Artifact writer for artifact."""
    def ensure_directories(self) -> None:
        """Ensure directories."""
        ...

    def frames_dir(self) -> Path:
        """Frames dir.
        
        Returns:
            Path: Result produced by frames dir.
        """
        ...

    def write_text(self, name: str, text: str) -> ArtifactRecord:
        """Write text.
        
        Args:
            name (str): Value for name.
            text (str): Value for text.
        
        Returns:
            ArtifactRecord: Result produced by write text.
        """
        ...

    def write_json(self, name: str, payload: Any) -> ArtifactRecord:
        """Write json.
        
        Args:
            name (str): Value for name.
            payload (Any): Value for payload.
        
        Returns:
            ArtifactRecord: Result produced by write json.
        """
        ...

    def register_file(self, name: str, path: Path, kind: str) -> ArtifactRecord:
        """Register file.
        
        Args:
            name (str): Value for name.
            path (Path): Filesystem path for the target resource.
            kind (str): Value for kind.
        
        Returns:
            ArtifactRecord: Result produced by register file.
        """
        ...
