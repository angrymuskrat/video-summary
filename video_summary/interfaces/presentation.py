from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, SceneSegment


class PresentationGenerator(Protocol):
    def generate(self, slides: list[SceneSegment], title: str, config: PipelineConfig) -> list[ArtifactRecord]:
        ...
