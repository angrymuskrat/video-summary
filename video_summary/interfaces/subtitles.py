from __future__ import annotations

from typing import Protocol

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, MediaMetadata, Utterance


class SubtitleGenerator(Protocol):
    def generate(
        self,
        subtitles: list[Utterance],
        metadata: MediaMetadata,
        config: PipelineConfig,
    ) -> list[ArtifactRecord]:
        ...
