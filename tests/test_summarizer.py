"""Tests for summarizer behavior in the video summary package."""


from video_summary.adapters.summarization import BasicSummarizer, OpenAISummarizer
from video_summary.adapters.summarization.openai import OpenAIRequest
from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, Utterance


RUSSIAN_ACTION = (
    "\u041d\u0443\u0436\u043d\u043e \u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u0438\u0442\u044c "
    "\u043d\u043e\u0432\u044b\u0439 \u043e\u0442\u0447\u0435\u0442 \u043a \u043f\u044f\u0442\u043d\u0438\u0446\u0435"
)
RUSSIAN_PREFIX = (
    "\u041d\u0443\u0436\u043d\u043e \u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u0438\u0442\u044c "
    "\u043d\u043e\u0432\u044b\u0439 \u043e\u0442\u0447\u0435\u0442"
)


def test_basic_summarizer_extracts_action_items_from_russian_and_english_markers(tmp_path) -> None:
    """Test that basic summarizer extracts action items from russian and english markers."""
    input_path = tmp_path / "meeting.webm"
    input_path.write_text("video", encoding="utf-8")
    config = PipelineConfig.from_paths(str(input_path), str(tmp_path / "out"))

    summarizer = BasicSummarizer()
    result = summarizer.summarize(
        utterances=[
            Utterance(0.0, 1.0, 1, RUSSIAN_ACTION),
            Utterance(1.0, 2.0, 2, "We should follow up with the vendor tomorrow"),
            Utterance(2.0, 3.0, 1, "General discussion"),
        ],
        slides=[SceneSegment(1, 0.0, 3.0, "frame.jpg", "slide text", 3)],
        config=config,
    )

    assert result.title == "Meeting summary for meeting"
    assert any(RUSSIAN_PREFIX in item for item in result.action_items)
    assert any("follow up with the vendor" in item for item in result.action_items)


def test_openai_summarizer_uses_server_settings_and_transcript_only(tmp_path) -> None:
    """Test that the OpenAI summarizer uses transcript-only content and server-side settings."""
    input_path = tmp_path / "meeting.webm"
    input_path.write_text("video", encoding="utf-8")
    config = PipelineConfig.from_paths(
        str(input_path),
        str(tmp_path / "out"),
        summarizer_provider="openai",
        openai_api_key="secret",
        openai_model="gpt-test-mini",
        openai_base_url="https://example.test/v1",
    )
    captured: list[OpenAIRequest] = []

    def fake_transport(payload: OpenAIRequest) -> str:
        captured.append(payload)
        return '{"title":"LLM title","overview":"Transcript only","bullet_points":["one"],"action_items":["two"]}'

    summarizer = OpenAISummarizer(transport=fake_transport)
    result = summarizer.summarize(
        utterances=[
            Utterance(0.0, 1.0, 1, "Launch plan"),
            Utterance(1.0, 2.0, 2, "Follow up with legal"),
        ],
        slides=[SceneSegment(1, 0.0, 2.0, "slide.jpg", "ignored slide text", 2)],
        config=config,
    )

    assert result.title == "LLM title"
    assert result.action_items == ["two"]
    assert captured[0].model == "gpt-test-mini"
    assert captured[0].base_url == "https://example.test/v1"
    assert "Speaker 1: Launch plan" in captured[0].transcript
    assert "ignored slide text" not in captured[0].transcript
