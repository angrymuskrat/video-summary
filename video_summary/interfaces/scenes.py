from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import MediaMetadata, SceneAnalysis


class SceneDetector(Protocol):
    def detect(self, video_path: str, metadata: MediaMetadata, config: PipelineConfig) -> SceneAnalysis:
        ...
