"""Protocol definitions for diarization components."""


from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import SpeakerTurn


class DiarizationEngine(Protocol):
    """Engine for diarization."""
    def diarize(self, audio_path: str, config: PipelineConfig) -> list[SpeakerTurn]:
        """Diarize the requested pipeline data.
        
        Args:
            audio_path (str): Filesystem path for audio.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            list[SpeakerTurn]: Result produced by diarize.
        """
        ...
