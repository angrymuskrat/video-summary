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
    def __init__(self, source: InputSource) -> None:
        self.source = source

    def load(self, config: PipelineConfig) -> InputSource:
        return self.source


class FakePreparator:
    def __init__(self, prepared: PreparedMedia) -> None:
        self.prepared = prepared

    def prepare(self, source: InputSource, config: PipelineConfig) -> PreparedMedia:
        return self.prepared


class FakeAsr:
    def transcribe(self, audio_path: str, config: PipelineConfig):
        return [WordToken(0.0, 0.5, "hello")], {"model": "fake"}


class FakeDiarization:
    def diarize(self, audio_path: str, config: PipelineConfig):
        return [SpeakerTurn(0.0, 1.0, 1)]


class FakeAlignment:
    def align(self, words, turns, config):
        return AlignmentResult(
            words=[WordToken(0.0, 0.5, "hello", 1)],
            utterances=[Utterance(0.0, 0.5, 1, "hello")],
            subtitles=[Utterance(0.0, 0.5, 1, "[1] hello")],
        )


class FakeScenes:
    def detect(self, video_path: str, metadata: MediaMetadata, config: PipelineConfig):
        return SceneAnalysis(scenes=[SceneBoundary(0.0, 1.0)], has_presentation=True)


class FakeSlides:
    def bind(self, scene_analysis, utterances, prepared_media, config):
        frame = config.layout().frames_dir / "scene_001.jpg"
        frame.parent.mkdir(parents=True, exist_ok=True)
        frame.write_text("frame", encoding="utf-8")
        return [SceneSegment(1, 0.0, 1.0, str(frame), "[1] hello", 1)]


class FakeSummarizer:
    def summarize(self, utterances, slides, config):
        return SummaryResult("Summary", "overview", ["hello"], ["follow up"])


class FakeSubtitles:
    def generate(self, subtitles, metadata, config):
        layout = config.layout()
        layout.subtitles_srt.write_text("1\n00:00:00,000 --> 00:00:00,500\n[1] hello\n", encoding="utf-8")
        layout.subtitles_ass.write_text("[Script Info]\n", encoding="utf-8")
        return [
            ArtifactRecord("subtitles_srt", str(layout.subtitles_srt), "text"),
            ArtifactRecord("subtitles_ass", str(layout.subtitles_ass), "text"),
        ]


class FakePresentation:
    def generate(self, slides, title, config):
        layout = config.layout()
        layout.slides_pptx.write_text("pptx", encoding="utf-8")
        return [ArtifactRecord("slides_pptx", str(layout.slides_pptx), "presentation")]


class FakeRenderer:
    def render(self, prepared_media, config):
        layout = config.layout()
        layout.video_subtitled_mp4.write_text("video", encoding="utf-8")
        return [ArtifactRecord("video_subtitled", str(layout.video_subtitled_mp4), "video")]


def make_config(tmp_path, *, start_from: str = "prepare") -> PipelineConfig:
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
    pipeline = make_pipeline(tmp_path)

    state = pipeline.run()

    assert state.summary is not None
    assert "summary" in state.artifacts.items
    assert Path(state.artifacts.items["transcript_json"].path).exists()


def test_orchestrator_can_resume_from_write_step(tmp_path) -> None:
    initial = make_pipeline(tmp_path)
    initial.run()

    resumed = make_pipeline(tmp_path, start_from="write")
    state = resumed.run()

    assert Path(state.artifacts.items["video_subtitled"].path).exists()
