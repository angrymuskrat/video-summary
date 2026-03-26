import json

from video_summary.adapters.readers import FilesystemInputReader
from video_summary.adapters.state_store import FilesystemStateStore
from video_summary.adapters.writers import FilesystemArtifactWriter
from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource, PipelineState


def make_config(tmp_path):
    input_path = tmp_path / "meeting.webm"
    input_path.write_text("video", encoding="utf-8")
    return PipelineConfig.from_paths(str(input_path), str(tmp_path / "out"))


def test_filesystem_input_reader_returns_resolved_source(tmp_path) -> None:
    config = make_config(tmp_path)

    source = FilesystemInputReader().load(config)

    assert source.video_path.endswith("meeting.webm")
    assert source.title == "meeting"


def test_filesystem_artifact_writer_writes_named_artifacts(tmp_path) -> None:
    config = make_config(tmp_path)
    writer = FilesystemArtifactWriter(config)
    writer.ensure_directories()

    record = writer.write_text("summary", "# Summary\n")
    json_record = writer.write_json("transcript_json", {"ok": True})

    assert record.path.endswith("summary.md")
    assert json.loads(config.layout().transcript_json.read_text(encoding="utf-8")) == {"ok": True}
    assert json_record.kind == "json"


def test_filesystem_state_store_roundtrip(tmp_path) -> None:
    config = make_config(tmp_path)
    store = FilesystemStateStore(config)
    state = PipelineState(input_source=InputSource(video_path="video.mp4", title="video"))

    store.save(state)
    restored = store.load()

    assert restored.input_source.video_path == "video.mp4"
