from video_summary.domain.models import (
    AlignmentResult,
    ArtifactRecord,
    InputSource,
    MediaMetadata,
    PipelineArtifacts,
    PipelineState,
    PreparedMedia,
    SceneAnalysis,
    SceneBoundary,
    SceneSegment,
    SpeakerTurn,
    SummaryResult,
    Utterance,
    WordToken,
)


def test_pipeline_state_roundtrip() -> None:
    state = PipelineState(
        input_source=InputSource(video_path="video.mp4", title="video"),
        prepared_media=PreparedMedia(
            video_path="work.mp4",
            audio_path="audio.wav",
            metadata=MediaMetadata(duration_sec=42.0, width=1920, height=1080, fps=25.0),
        ),
        asr_meta={"model": "tiny"},
        asr_words=[WordToken(0.0, 0.5, "hello", 1)],
        speaker_turns=[SpeakerTurn(0.0, 1.0, 1)],
        alignment=AlignmentResult(
            words=[WordToken(0.0, 0.5, "hello", 1)],
            utterances=[Utterance(0.0, 0.5, 1, "hello")],
            subtitles=[Utterance(0.0, 0.5, 1, "[1] hello")],
        ),
        scene_analysis=SceneAnalysis(scenes=[SceneBoundary(0.0, 10.0)], has_presentation=True),
        slide_segments=[SceneSegment(1, 0.0, 10.0, "frame.jpg", "hello", 1)],
        summary=SummaryResult("title", "overview", ["point"], ["action"]),
        transcript_json="transcript.json",
        artifacts=PipelineArtifacts(items={"summary": ArtifactRecord("summary", "summary.md", "text")}),
    )

    restored = PipelineState.from_dict(state.to_dict())

    assert restored.to_dict() == state.to_dict()


def test_pipeline_state_supports_legacy_monolith_shape() -> None:
    legacy = {
        "state_version": 1,
        "input_video": "video.mp4",
        "duration_sec": 15.0,
        "video": {"width": 1280, "height": 720, "fps": 30.0},
        "asr_meta": {"model_name": "base"},
        "asr_words": [{"start": 0.0, "end": 0.5, "text": "hello", "speaker": None}],
        "speaker_turns": [{"start": 0.0, "end": 1.0, "speaker": 1}],
        "words": [{"start": 0.0, "end": 0.5, "text": "hello", "speaker": 1}],
        "utterances": [{"start": 0.0, "end": 0.5, "speaker": 1, "text": "hello"}],
        "subtitles": [{"start": 0.0, "end": 0.5, "speaker": 1, "text": "[1] hello"}],
        "scenes": [[0.0, 10.0]],
        "has_presentation": True,
        "slide_segments": [{"index": 1, "start": 0.0, "end": 10.0, "frame_path": "frame.jpg", "text": "hello", "utterance_count": 1}],
        "transcript_json": "transcript.json",
    }

    state = PipelineState.from_dict(legacy)

    assert state.input_source.video_path == "video.mp4"
    assert state.prepared_media.metadata.width == 1280
    assert state.alignment is not None
    assert state.alignment.utterances[0].text == "hello"
    assert state.scene_analysis is not None
    assert state.scene_analysis.has_presentation is True
