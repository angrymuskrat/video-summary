from video_summary.adapters.summarization import BasicSummarizer
from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, Utterance


def test_basic_summarizer_extracts_action_items_from_russian_and_english_markers(tmp_path) -> None:
    input_path = tmp_path / "meeting.webm"
    input_path.write_text("video", encoding="utf-8")
    config = PipelineConfig.from_paths(str(input_path), str(tmp_path / "out"))

    summarizer = BasicSummarizer()
    result = summarizer.summarize(
        utterances=[
            Utterance(0.0, 1.0, 1, "Нужно подготовить новый отчет к пятнице"),
            Utterance(1.0, 2.0, 2, "We should follow up with the vendor tomorrow"),
            Utterance(2.0, 3.0, 1, "General discussion"),
        ],
        slides=[SceneSegment(1, 0.0, 3.0, "frame.jpg", "slide text", 3)],
        config=config,
    )

    assert result.title == "Meeting summary for meeting"
    assert any("Нужно подготовить новый отчет" in item for item in result.action_items)
    assert any("follow up with the vendor" in item for item in result.action_items)
