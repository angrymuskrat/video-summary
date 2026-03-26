from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from video_summary.domain.models import ArtifactRecord


class ArtifactWriter(Protocol):
    def ensure_directories(self) -> None:
        ...

    def frames_dir(self) -> Path:
        ...

    def write_text(self, name: str, text: str) -> ArtifactRecord:
        ...

    def write_json(self, name: str, payload: Any) -> ArtifactRecord:
        ...

    def register_file(self, name: str, path: Path, kind: str) -> ArtifactRecord:
        ...
