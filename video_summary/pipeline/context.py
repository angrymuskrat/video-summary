"""Runtime context object shared across pipeline steps during execution."""


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
    """Context object for pipeline.
    
    Attributes:
        config (PipelineConfig): Stored value for config.
        input_reader (InputReader): Stored value for input reader.
        artifact_writer (ArtifactWriter): Stored value for artifact writer.
        state_store (StateStore): Stored value for state store.
        media_preparator (MediaPreparator): Stored value for media preparator.
        asr_engine (ASREngine): Stored value for asr engine.
        diarization_engine (DiarizationEngine): Stored value for diarization engine.
        alignment_engine (AlignmentEngine): Stored value for alignment engine.
        scene_detector (SceneDetector): Stored value for scene detector.
        slide_binder (SlideBinder): Stored value for slide binder.
        summarizer (Summarizer): Stored value for summarizer.
        subtitle_generator (SubtitleGenerator): Stored value for subtitle generator.
        presentation_generator (PresentationGenerator): Stored value for presentation generator.
        video_renderer (VideoRenderer): Stored value for video renderer.
        state (PipelineState): Stored value for state.
    """
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
        """Register artifacts.
        
        Args:
            records (list[ArtifactRecord]): Value for records.
        """
        for record in records:
            self.state.artifacts.items[record.name] = record

    def require_prepared_media(self) -> PreparedMedia:
        """Return the required prepared media.
        
        Returns:
            PreparedMedia: Result produced by require prepared media.
        """
        if self.state.prepared_media is None:
            raise RuntimeError("Prepared media is missing. Run or restore the 'prepare' step first.")
        return self.state.prepared_media

    def require_alignment(self) -> AlignmentResult:
        """Return the required alignment.
        
        Returns:
            AlignmentResult: Result produced by require alignment.
        """
        if self.state.alignment is None:
            raise RuntimeError("Alignment result is missing. Run or restore the 'align' step first.")
        return self.state.alignment

    def require_scene_analysis(self) -> SceneAnalysis:
        """Return the required scene analysis.
        
        Returns:
            SceneAnalysis: Result produced by require scene analysis.
        """
        if self.state.scene_analysis is None:
            raise RuntimeError("Scene analysis is missing. Run or restore the 'scenes' step first.")
        return self.state.scene_analysis

    def require_summary(self) -> SummaryResult:
        """Return the required summary.
        
        Returns:
            SummaryResult: Result produced by require summary.
        """
        if self.state.summary is None:
            raise RuntimeError("Summary is missing. Run or restore the 'summarize' step first.")
        return self.state.summary
