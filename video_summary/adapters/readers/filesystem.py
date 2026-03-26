"""Concrete implementation of input reading for the video summary pipeline."""


from __future__ import annotations

from pathlib import Path

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource


class FilesystemInputReader:
    """Input reader for filesystem input."""
    def load(self, config: PipelineConfig) -> InputSource:
        """Load the requested pipeline data.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            InputSource: Result produced by load.
        """
        input_path = Path(config.input_path).expanduser().resolve()
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        audio_path = Path(config.audio_path).expanduser().resolve() if config.audio_path else None
        if audio_path and not audio_path.exists():
            raise FileNotFoundError(audio_path)
        return InputSource(
            video_path=str(input_path),
            audio_path=str(audio_path) if audio_path else None,
            title=input_path.stem,
        )
