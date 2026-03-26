from __future__ import annotations

from typing import Any, Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import WordToken


class ASREngine(Protocol):
    def transcribe(self, audio_path: str, config: PipelineConfig) -> tuple[list[WordToken], dict[str, Any]]:
        ...
