from __future__ import annotations

from pathlib import Path
from typing import Any

from video_summary.domain.models import ArtifactRecord


class DatabaseArtifactWriter:
    def ensure_directories(self) -> None:
        return None

    def frames_dir(self) -> Path:
        raise NotImplementedError("DB-backed frame storage is not implemented yet.")

    def write_text(self, name: str, text: str) -> ArtifactRecord:
        raise NotImplementedError(
            "DatabaseArtifactWriter is a contract placeholder. "
            "Implement DB persistence here without changing the orchestrator."
        )

    def write_json(self, name: str, payload: Any) -> ArtifactRecord:
        raise NotImplementedError(
            "DatabaseArtifactWriter is a contract placeholder. "
            "Implement DB persistence here without changing the orchestrator."
        )

    def register_file(self, name: str, path: Path, kind: str) -> ArtifactRecord:
        raise NotImplementedError(
            "DatabaseArtifactWriter is a contract placeholder. "
            "Implement DB persistence here without changing the orchestrator."
        )
