"""Pipeline assembly and orchestration logic for the default meeting-processing flow."""


from __future__ import annotations

import shutil

from video_summary.config import PipelineConfig
from video_summary.domain.models import PipelineState
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
from video_summary.pipeline.context import PipelineContext
from video_summary.pipeline.steps import (
    AlignStep,
    BindSlidesStep,
    DetectScenesStep,
    DiarizeStep,
    PrepareStep,
    RenderVideoStep,
    SummarizeStep,
    TranscribeStep,
    WriteOutputsStep,
)


class MeetingPipeline:
    """Meeting pipeline."""
    def __init__(
        self,
        config: PipelineConfig,
        *,
        input_reader: InputReader,
        artifact_writer: ArtifactWriter,
        state_store: StateStore,
        media_preparator: MediaPreparator,
        asr_engine: ASREngine,
        diarization_engine: DiarizationEngine,
        alignment_engine: AlignmentEngine,
        scene_detector: SceneDetector,
        slide_binder: SlideBinder,
        summarizer: Summarizer,
        subtitle_generator: SubtitleGenerator,
        presentation_generator: PresentationGenerator,
        video_renderer: VideoRenderer,
    ) -> None:
        """Initialize the meeting pipeline.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
            input_reader (InputReader): Keyword-only value for input reader.
            artifact_writer (ArtifactWriter): Keyword-only value for artifact writer.
            state_store (StateStore): Keyword-only value for state store.
            media_preparator (MediaPreparator): Keyword-only value for media preparator.
            asr_engine (ASREngine): Keyword-only value for asr engine.
            diarization_engine (DiarizationEngine): Keyword-only value for diarization engine.
            alignment_engine (AlignmentEngine): Keyword-only value for alignment engine.
            scene_detector (SceneDetector): Keyword-only value for scene detector.
            slide_binder (SlideBinder): Keyword-only value for slide binder.
            summarizer (Summarizer): Keyword-only value for summarizer.
            subtitle_generator (SubtitleGenerator): Keyword-only value for subtitle generator.
            presentation_generator (PresentationGenerator): Keyword-only value for presentation generator.
            video_renderer (VideoRenderer): Keyword-only value for video renderer.
        """
        self.config = config
        self.input_reader = input_reader
        self.artifact_writer = artifact_writer
        self.state_store = state_store
        self.media_preparator = media_preparator
        self.asr_engine = asr_engine
        self.diarization_engine = diarization_engine
        self.alignment_engine = alignment_engine
        self.scene_detector = scene_detector
        self.slide_binder = slide_binder
        self.summarizer = summarizer
        self.subtitle_generator = subtitle_generator
        self.presentation_generator = presentation_generator
        self.video_renderer = video_renderer
        self.steps = [
            PrepareStep(),
            TranscribeStep(),
            DiarizeStep(),
            AlignStep(),
            DetectScenesStep(),
            BindSlidesStep(),
            SummarizeStep(),
            WriteOutputsStep(),
            RenderVideoStep(),
        ]

    def run(self) -> PipelineState:
        """Run the configured pipeline.
        
        Returns:
            PipelineState: Result produced by run.
        """
        self.artifact_writer.ensure_directories()
        input_source = self.input_reader.load(self.config)

        if self.config.start_from != "prepare":
            state = self.state_store.load()
            state.require_input_match(input_source.video_path)
        else:
            state = PipelineState(input_source=input_source, start_from=self.config.start_from)

        if state.input_source is None:
            state.input_source = input_source
        if state.prepared_media is not None:
            if not state.prepared_media.video_path:
                state.prepared_media.video_path = str(self.config.layout().work_video)
            if not state.prepared_media.audio_path:
                state.prepared_media.audio_path = str(self.config.layout().audio_wav)

        context = PipelineContext(
            config=self.config,
            input_reader=self.input_reader,
            artifact_writer=self.artifact_writer,
            state_store=self.state_store,
            media_preparator=self.media_preparator,
            asr_engine=self.asr_engine,
            diarization_engine=self.diarization_engine,
            alignment_engine=self.alignment_engine,
            scene_detector=self.scene_detector,
            slide_binder=self.slide_binder,
            summarizer=self.summarizer,
            subtitle_generator=self.subtitle_generator,
            presentation_generator=self.presentation_generator,
            video_renderer=self.video_renderer,
            state=state,
        )

        for step in self.steps:
            if self.config.step_enabled(step.name):
                step.run(context)
                context.state.start_from = step.name
                self.state_store.save(context.state)

        if not self.config.keep_work_files:
            shutil.rmtree(self.config.layout().work_dir, ignore_errors=True)

        return context.state


def build_default_pipeline(
    config: PipelineConfig,
    *,
    input_reader: InputReader | None = None,
    artifact_writer: ArtifactWriter | None = None,
    state_store: StateStore | None = None,
    media_preparator: MediaPreparator | None = None,
    asr_engine: ASREngine | None = None,
    diarization_engine: DiarizationEngine | None = None,
    alignment_engine: AlignmentEngine | None = None,
    scene_detector: SceneDetector | None = None,
    slide_binder: SlideBinder | None = None,
    summarizer: Summarizer | None = None,
    subtitle_generator: SubtitleGenerator | None = None,
    presentation_generator: PresentationGenerator | None = None,
    video_renderer: VideoRenderer | None = None,
) -> MeetingPipeline:
    # Keep provider-specific imports lazy so package imports and unit tests
    # do not require optional heavy backends until the defaults are instantiated.
    """Build the default pipeline with concrete adapters.
    
    Args:
        config (PipelineConfig): Pipeline configuration to use for the operation.
        input_reader (InputReader | None): Optional keyword-only value for input reader.
        artifact_writer (ArtifactWriter | None): Optional keyword-only value for artifact writer.
        state_store (StateStore | None): Optional keyword-only value for state store.
        media_preparator (MediaPreparator | None): Optional keyword-only value for media preparator.
        asr_engine (ASREngine | None): Optional keyword-only value for asr engine.
        diarization_engine (DiarizationEngine | None): Optional keyword-only value for diarization engine.
        alignment_engine (AlignmentEngine | None): Optional keyword-only value for alignment engine.
        scene_detector (SceneDetector | None): Optional keyword-only value for scene detector.
        slide_binder (SlideBinder | None): Optional keyword-only value for slide binder.
        summarizer (Summarizer | None): Optional keyword-only value for summarizer.
        subtitle_generator (SubtitleGenerator | None): Optional keyword-only value for subtitle generator.
        presentation_generator (PresentationGenerator | None): Optional keyword-only value for presentation generator.
        video_renderer (VideoRenderer | None): Optional keyword-only value for video renderer.
    
    Returns:
        MeetingPipeline: Result produced by build default pipeline.
    """
    from video_summary.adapters.alignment import DefaultAlignmentEngine
    from video_summary.adapters.asr import FasterWhisperASR
    from video_summary.adapters.diarization import PyannoteDiarization
    from video_summary.adapters.media import FFmpegMediaPreparator
    from video_summary.adapters.presentation import PptxPresentationGenerator
    from video_summary.adapters.readers import FilesystemInputReader
    from video_summary.adapters.rendering import FFmpegVideoRenderer
    from video_summary.adapters.scenes import PySceneDetectSceneDetector
    from video_summary.adapters.slide_binding import DefaultSlideBinder
    from video_summary.adapters.state_store import FilesystemStateStore
    from video_summary.adapters.subtitles import StandardSubtitleGenerator
    from video_summary.adapters.summarization import BasicSummarizer
    from video_summary.adapters.writers import FilesystemArtifactWriter

    return MeetingPipeline(
        config,
        input_reader=input_reader or FilesystemInputReader(),
        artifact_writer=artifact_writer or FilesystemArtifactWriter(config),
        state_store=state_store or FilesystemStateStore(config),
        media_preparator=media_preparator or FFmpegMediaPreparator(),
        asr_engine=asr_engine or FasterWhisperASR(),
        diarization_engine=diarization_engine or PyannoteDiarization(),
        alignment_engine=alignment_engine or DefaultAlignmentEngine(),
        scene_detector=scene_detector or PySceneDetectSceneDetector(),
        slide_binder=slide_binder or DefaultSlideBinder(),
        summarizer=summarizer or BasicSummarizer(),
        subtitle_generator=subtitle_generator or StandardSubtitleGenerator(),
        presentation_generator=presentation_generator or PptxPresentationGenerator(),
        video_renderer=video_renderer or FFmpegVideoRenderer(),
    )
