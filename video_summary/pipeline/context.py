from __future__ import annotations

from dataclasses import dataclass

from video_summary.config import PipelineConfig
from video_summary.domain.models import (
    AlignmentResult,
    ArtifactRecord,
    PipelineState,
    PreparedMedia,
    SceneAnalysis,
    SummaryResult,
)
from video_summary.interfaces import (
    ASREngine,
    AlignmentEngine,
    ArtifactWriter,
    DiarizationEngine,
    InputReader,
    MediaPreparator,
    PresentationGenerator,
    SceneDetector,
    SlideBinder,
    StateStore,
    SubtitleGenerator,
    Summarizer,
    VideoRenderer,
)


@dataclass
class PipelineContext:
    config: PipelineConfig
    input_reader: InputReader
    artifact_writer: ArtifactWriter
    state_store: StateStore
    media_preparator: MediaPreparator
    asr_engine: ASREngine
    diarization_engine: DiarizationEngine
    alignment_engine: AlignmentEngine
    scene_detector: SceneDetector
    slide_binder: SlideBinder
    summarizer: Summarizer
    subtitle_generator: SubtitleGenerator
    presentation_generator: PresentationGenerator
    video_renderer: VideoRenderer
    state: PipelineState

    def register_artifacts(self, records: list[ArtifactRecord]) -> None:
        for record in records:
            self.state.artifacts.items[record.name] = record

    def require_prepared_media(self) -> PreparedMedia:
        if self.state.prepared_media is None:
            raise RuntimeError("Prepared media is missing. Run or restore the 'prepare' step first.")
        return self.state.prepared_media

    def require_alignment(self) -> AlignmentResult:
        if self.state.alignment is None:
            raise RuntimeError("Alignment result is missing. Run or restore the 'align' step first.")
        return self.state.alignment

    def require_scene_analysis(self) -> SceneAnalysis:
        if self.state.scene_analysis is None:
            raise RuntimeError("Scene analysis is missing. Run or restore the 'scenes' step first.")
        return self.state.scene_analysis

    def require_summary(self) -> SummaryResult:
        if self.state.summary is None:
            raise RuntimeError("Summary is missing. Run or restore the 'summarize' step first.")
        return self.state.summary
