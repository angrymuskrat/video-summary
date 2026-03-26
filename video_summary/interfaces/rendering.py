from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, PreparedMedia


class VideoRenderer(Protocol):
    def render(self, prepared_media: PreparedMedia, config: PipelineConfig) -> list[ArtifactRecord]:
        ...
