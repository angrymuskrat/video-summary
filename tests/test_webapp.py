"""Tests for the web application wrapper, job lifecycle, and retention cleanup."""


from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from video_summary.config import PipelineConfig
from video_summary.domain.models import PipelineArtifacts, PipelineState, SummaryResult
from video_summary.webapp.app import create_app
from video_summary.webapp.database import create_session_factory, init_database
from video_summary.webapp.models import JobEntity
from video_summary.webapp.repository import JobStore, utc_now
from video_summary.webapp.service import JobSubmission
from video_summary.webapp.settings import AppSettings


def test_job_submission_maps_server_side_openai_settings(tmp_path) -> None:
    """Test that browser form values map into the core pipeline config correctly."""
    submission = JobSubmission.from_form(
        language="ru",
        device="cpu",
        summarizer_provider="openai",
        export_pdf=True,
    )
    settings = AppSettings(
        database_url="sqlite+pysqlite:///unused.db",
        storage_root=tmp_path / "data",
        openai_api_key="secret",
        openai_model="gpt-test-mini",
        openai_base_url="https://example.test/v1",
    )

    config = submission.to_pipeline_config(
        input_path=tmp_path / "meeting.webm",
        output_dir=tmp_path / "out",
        settings=settings,
    )

    assert config.language == "ru"
    assert config.device == "cpu"
    assert config.summarizer_provider == "openai"
    assert config.export_pdf is True
    assert config.openai_api_key == "secret"
    assert config.openai_model == "gpt-test-mini"
    assert config.openai_base_url == "https://example.test/v1"


def test_webapp_job_lifecycle_and_artifact_download(tmp_path) -> None:
    """Test upload -> job id -> status -> artifact download with a stub pipeline."""
    settings = AppSettings(
        database_url=f"sqlite+pysqlite:///{(tmp_path / 'app.db').as_posix()}",
        storage_root=tmp_path / "data",
        cleanup_interval_seconds=0,
    )

    def fake_pipeline_factory(config, *, input_reader, artifact_writer, state_store, **_kwargs):
        class FakePipeline:
            def run(self_nonlocal):
                source = input_reader.load(config)
                artifact_writer.ensure_directories()
                summary_record = artifact_writer.write_text("summary", "# Summary\n\nProcessed transcript.\n")
                json_record = artifact_writer.write_json("transcript_json", {"status": "ok"})
                state = PipelineState(
                    input_source=source,
                    start_from="write",
                    summary=SummaryResult("Summary", "Processed transcript."),
                    artifacts=PipelineArtifacts(
                        items={
                            "summary": summary_record,
                            "transcript_json": json_record,
                        }
                    ),
                )
                state_store.save(state)
                return state

        return FakePipeline()

    with TestClient(create_app(settings=settings, pipeline_factory=fake_pipeline_factory)) as client:
        response = client.post(
            "/api/jobs",
            files={"file": ("meeting.webm", b"video-bytes", "video/webm")},
            data={"language": "ru", "summarizer_provider": "basic"},
        )
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        deadline = time.monotonic() + 5
        payload = {}
        while time.monotonic() < deadline:
            payload = client.get(f"/api/jobs/{job_id}").json()
            if payload["status"] == "completed":
                break
            time.sleep(0.05)

        assert payload["status"] == "completed"
        assert payload["pipeline_config"]["language"] == "ru"
        assert any(item["name"] == "summary" for item in payload["artifacts"])

        artifact_response = client.get(f"/api/jobs/{job_id}/artifacts/summary")
        assert artifact_response.status_code == 200
        assert "Processed transcript" in artifact_response.text


def test_retention_cleanup_removes_expired_job_records_and_files(tmp_path) -> None:
    """Test that cleanup deletes expired job rows and managed job directories."""
    settings = AppSettings(
        database_url=f"sqlite+pysqlite:///{(tmp_path / 'cleanup.db').as_posix()}",
        storage_root=tmp_path / "data",
        cleanup_interval_seconds=0,
    )

    def fake_pipeline_factory(config, *, input_reader, artifact_writer, state_store, **_kwargs):
        class FakePipeline:
            def run(self_nonlocal):
                source = input_reader.load(config)
                artifact_writer.ensure_directories()
                summary_record = artifact_writer.write_text("summary", "cleanup me")
                state = PipelineState(
                    input_source=source,
                    start_from="write",
                    summary=SummaryResult("Summary", "cleanup me"),
                    artifacts=PipelineArtifacts(items={"summary": summary_record}),
                )
                state_store.save(state)
                return state

        return FakePipeline()

    with TestClient(create_app(settings=settings, pipeline_factory=fake_pipeline_factory)) as client:
        response = client.post(
            "/api/jobs",
            files={"file": ("meeting.webm", b"video-bytes", "video/webm")},
        )
        job_id = response.json()["job_id"]
        job_root = settings.storage_root / "jobs" / job_id

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            payload = client.get(f"/api/jobs/{job_id}").json()
            if payload["status"] == "completed":
                break
            time.sleep(0.05)

        session_factory = create_session_factory(settings.database_url)
        init_database(session_factory)
        session: Session = session_factory()
        try:
            job = session.get(JobEntity, job_id)
            assert job is not None
            job.expires_at = utc_now() - timedelta(hours=1)
            session.commit()
        finally:
            session.close()

        cleanup_response = client.get(f"/api/jobs/{job_id}")
        assert cleanup_response.status_code == 404
        assert not job_root.exists()
