"""Concrete implementation of artifact writing for the video summary pipeline."""


from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord


class FilesystemArtifactWriter:
    """Artifact writer for filesystem artifact."""
    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the filesystem artifact writer.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        """
        self._layout = config.layout()

    def ensure_directories(self) -> None:
        """Ensure directories."""
        self._layout.output_dir.mkdir(parents=True, exist_ok=True)
        self._layout.work_dir.mkdir(parents=True, exist_ok=True)
        self._layout.frames_dir.mkdir(parents=True, exist_ok=True)

    def frames_dir(self) -> Path:
        """Frames dir.
        
        Returns:
            Path: Result produced by frames dir.
        """
        self._layout.frames_dir.mkdir(parents=True, exist_ok=True)
        return self._layout.frames_dir

    def _path_for(self, name: str) -> Path:
        """Path for.
        
        Args:
            name (str): Value for name.
        
        Returns:
            Path: Result produced by path for.
        """
        mapping = {
            "transcript": self._layout.transcript_txt,
            "transcript_with_roles": self._layout.transcript_with_roles_txt,
            "summary": self._layout.summary_md,
            "transcript_json": self._layout.transcript_json,
            "subtitles_srt": self._layout.subtitles_srt,
            "subtitles_ass": self._layout.subtitles_ass,
            "video_subtitled": self._layout.video_subtitled_mp4,
            "video_softsubs": self._layout.video_softsubs_mp4,
            "slides_pptx": self._layout.slides_pptx,
            "slides_pdf": self._layout.slides_pdf,
        }
        if name not in mapping:
            raise KeyError(f"Unknown artifact name: {name}")
        return mapping[name]

    def write_text(self, name: str, text: str) -> ArtifactRecord:
        """Write text.
        
        Args:
            name (str): Value for name.
            text (str): Value for text.
        
        Returns:
            ArtifactRecord: Result produced by write text.
        """
        path = self._path_for(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return self.register_file(name, path, "text")

    def write_json(self, name: str, payload: Any) -> ArtifactRecord:
        """Write json.
        
        Args:
            name (str): Value for name.
            payload (Any): Value for payload.
        
        Returns:
            ArtifactRecord: Result produced by write json.
        """
        path = self._path_for(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.register_file(name, path, "json")

    def register_file(self, name: str, path: Path, kind: str) -> ArtifactRecord:
        """Register file.
        
        Args:
            name (str): Value for name.
            path (Path): Filesystem path for the target resource.
            kind (str): Value for kind.
        
        Returns:
            ArtifactRecord: Result produced by register file.
        """
        return ArtifactRecord(name=name, path=str(path), kind=kind)
