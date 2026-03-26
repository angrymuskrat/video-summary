"""Protocol definitions for asr components."""


from __future__ import annotations

from typing import Any, Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import WordToken


class ASREngine(Protocol):
    """Engine for a s r."""
    def transcribe(self, audio_path: str, config: PipelineConfig) -> tuple[list[WordToken], dict[str, Any]]:
        """Transcribe the requested pipeline data.
        
        Args:
            audio_path (str): Filesystem path for audio.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            tuple[list[WordToken], dict[str, Any]]: Result produced by transcribe.
        """
        ...
