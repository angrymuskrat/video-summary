"""Tests for orchestrator behavior in the video summary package."""


from pathlib import Path

from video_summary.config import PipelineConfig
from video_summary.domain.models import (
    AlignmentResult,
    ArtifactRecord,
    InputSource,
    MediaMetadata,
    PreparedMedia,
    SceneAnalysis,
    SceneBoundary,
    SceneSegment,
    SpeakerTurn,
    SummaryResult,
    Utterance,
    WordToken,
)
from video_summary.orchestrator import MeetingPipeline
from video_summary.adapters.state_store import FilesystemStateStore
from video_summary.adapters.writers import FilesystemArtifactWriter


class FakeReader:
    """Test double for reader."""
    def __init__(self, source: InputSource) -> None:
        """Initialize the fake reader.
        
        Args:
            source (InputSource): Value for source.
        """
        self.source = source

    def load(self, config: PipelineConfig) -> InputSource:
        """Load the requested pipeline data.
        
        Args:
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            InputSource: Result produced by load.
        """
        return self.source


class FakePreparator:
    """Test double for preparator."""
    def __init__(self, prepared: PreparedMedia) -> None:
        """Initialize the fake preparator.
        
        Args:
            prepared (PreparedMedia): Value for prepared.
        """
        self.prepared = prepared

    def prepare(self, source: InputSource, config: PipelineConfig) -> PreparedMedia:
        """Prepare the requested pipeline data.
        
        Args:
            source (InputSource): Value for source.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            PreparedMedia: Result produced by prepare.
        """
        return self.prepared


class FakeAsr:
    """Test double for asr."""
    def transcribe(self, audio_path: str, config: PipelineConfig):
        """Transcribe the requested pipeline data.
        
        Args:
            audio_path (str): Filesystem path for audio.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        """
        return [WordToken(0.0, 0.5, "hello")], {"model": "fake"}


class FakeDiarization:
    """Test double for diarization."""
    def diarize(self, audio_path: str, config: PipelineConfig):
        """Diarize the requested pipeline data.
        
        Args:
            audio_path (str): Filesystem path for audio.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        """
        return [SpeakerTurn(0.0, 1.0, 1)]


class FakeAlignment:
    """Test double for alignment."""
    def align(self, words, turns, config):
        """Align the requested pipeline data.
        
        Args:
            words: Value for words.
            turns: Value for turns.
            config: Pipeline configuration to use for the operation.
        """
        return AlignmentResult(
            words=[WordToken(0.0, 0.5, "hello", 1)],
            utterances=[Utterance(0.0, 0.5, 1, "hello")],
            subtitles=[Utterance(0.0, 0.5, 1, "[1] hello")],
        )


class FakeScenes:
    """Test double for scenes."""
    def detect(self, video_path: str, metadata: MediaMetadata, config: PipelineConfig):
        """Detect the requested pipeline data.
        
        Args:
            video_path (str): Filesystem path for video.
            metadata (MediaMetadata): Value for metadata.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        """
        return SceneAnalysis(scenes=[SceneBoundary(0.0, 1.0)], has_presentation=True)


class FakeSlides:
    """Test double for slides."""
    def bind(self, scene_analysis, utterances, prepared_media, config):
        """Bind the requested pipeline data.
        
        Args:
            scene_analysis: Value for scene analysis.
            utterances: Value for utterances.
            prepared_media: Value for prepared media.
            config: Pipeline configuration to use for the operation.
        """
        frame = config.layout().frames_dir / "scene_001.jpg"
        frame.parent.mkdir(parents=True, exist_ok=True)
        frame.write_text("frame", encoding="utf-8")
        return [SceneSegment(1, 0.0, 1.0, str(frame), "[1] hello", 1)]


class FakeSummarizer:
    """Test double for summarizer."""
    def summarize(self, utterances, slides, config):
        """Summarize the requested pipeline data.
        
        Args:
            utterances: Value for utterances.
            slides: Value for slides.
            config: Pipeline configuration to use for the operation.
        """
        return SummaryResult("Summary", "overview", ["hello"], ["follow up"])


class FakeSubtitles:
    """Test double for subtitles."""
    def generate(self, subtitles, metadata, config):
        """Generate the requested pipeline data.
        
        Args:
            subtitles: Value for subtitles.
            metadata: Value for metadata.
            config: Pipeline configuration to use for the operation.
        """
        layout = config.layout()
        layout.subtitles_srt.write_text("1\n00:00:00,000 --> 00:00:00,500\n[1] hello\n", encoding="utf-8")
        layout.subtitles_ass.write_text("[Script Info]\n", encoding="utf-8")
        return [
            ArtifactRecord("subtitles_srt", str(layout.subtitles_srt), "text"),
            ArtifactRecord("subtitles_ass", str(layout.subtitles_ass), "text"),
        ]


class FakePresentation:
    """Test double for presentation."""
    def generate(self, slides, title, config):
        """Generate the requested pipeline data.
        
        Args:
            slides: Value for slides.
            title: Value for title.
            config: Pipeline configuration to use for the operation.
        """
        layout = config.layout()
        layout.slides_pptx.write_text("pptx", encoding="utf-8")
        return [ArtifactRecord("slides_pptx", str(layout.slides_pptx), "presentation")]


class FakeRenderer:
    """Test double for renderer."""
    def render(self, prepared_media, config):
        """Render the requested pipeline data.
        
        Args:
            prepared_media: Value for prepared media.
            config: Pipeline configuration to use for the operation.
        """
        layout = config.layout()
        layout.video_subtitled_mp4.write_text("video", encoding="utf-8")
        return [ArtifactRecord("video_subtitled", str(layout.video_subtitled_mp4), "video")]


def make_config(tmp_path, *, start_from: str = "prepare") -> PipelineConfig:
    """Create config.
    
    Args:
        tmp_path: Temporary directory fixture provided by pytest.
        start_from (str): Optional keyword-only value for start from.
    
    Returns:
        PipelineConfig: Result produced by make config.
    """
    input_path = tmp_path / "meeting.webm"
    input_path.write_text("video", encoding="utf-8")
    return PipelineConfig.from_paths(
        str(input_path),
        str(tmp_path / "out"),
        hf_token="token",
        start_from=start_from,
        keep_work_files=True,
    )


def make_pipeline(tmp_path, *, start_from: str = "prepare") -> MeetingPipeline:
    """Create pipeline.
    
    Args:
        tmp_path: Temporary directory fixture provided by pytest.
        start_from (str): Optional keyword-only value for start from.
    
    Returns:
        MeetingPipeline: Result produced by make pipeline.
    """
    config = make_config(tmp_path, start_from=start_from)
    source = InputSource(video_path=str(config.input_path), title=config.input_path.stem)
    prepared = PreparedMedia(
        video_path=str(config.layout().work_video),
        audio_path=str(config.layout().audio_wav),
        metadata=MediaMetadata(1.0, 1280, 720, 30.0),
    )
    Path(prepared.video_path).parent.mkdir(parents=True, exist_ok=True)
    Path(prepared.video_path).write_text("video", encoding="utf-8")
    Path(prepared.audio_path).write_text("audio", encoding="utf-8")
    return MeetingPipeline(
        config,
        input_reader=FakeReader(source),
        artifact_writer=FilesystemArtifactWriter(config),
        state_store=FilesystemStateStore(config),
        media_preparator=FakePreparator(prepared),
        asr_engine=FakeAsr(),
        diarization_engine=FakeDiarization(),
        alignment_engine=FakeAlignment(),
        scene_detector=FakeScenes(),
        slide_binder=FakeSlides(),
        summarizer=FakeSummarizer(),
        subtitle_generator=FakeSubtitles(),
        presentation_generator=FakePresentation(),
        video_renderer=FakeRenderer(),
    )


def test_orchestrator_runs_full_pipeline_with_fakes(tmp_path) -> None:
    """Test that orchestrator runs full pipeline with fakes.
    
    Args:
        tmp_path: Temporary directory fixture provided by pytest.
    """
    pipeline = make_pipeline(tmp_path)

    state = pipeline.run()

    assert state.summary is not None
    assert "summary" in state.artifacts.items
    assert Path(state.artifacts.items["transcript_json"].path).exists()


def test_orchestrator_can_resume_from_write_step(tmp_path) -> None:
    """Test that orchestrator can resume from write step.
    
    Args:
        tmp_path: Temporary directory fixture provided by pytest.
    """
    initial = make_pipeline(tmp_path)
    initial.run()

    resumed = make_pipeline(tmp_path, start_from="write")
    state = resumed.run()

    assert Path(state.artifacts.items["video_subtitled"].path).exists()
