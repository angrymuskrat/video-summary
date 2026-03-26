"""Persistence helpers for API jobs, artifacts, and retention cleanup."""


from __future__ import annotations

import mimetypes
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from video_summary.adapters.readers.database import DatabaseInputRecord
from video_summary.webapp.models import ArtifactEntity, JobEntity


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ArtifactSnapshot:
    """Serializable artifact metadata returned by the API layer."""

    name: str
    kind: str
    path: str
    media_type: str | None
    size_bytes: int | None
    created_at: datetime
    exists: bool

    def to_dict(self, job_id: str) -> dict[str, Any]:
        """Convert the artifact snapshot into an API payload."""
        return {
            "name": self.name,
            "kind": self.kind,
            "path": self.path,
            "media_type": self.media_type,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at,
            "exists": self.exists,
            "download_url": f"/api/jobs/{job_id}/artifacts/{self.name}?download=1",
            "preview_url": f"/api/jobs/{job_id}/artifacts/{self.name}",
            "previewable": (self.media_type or "").startswith("text/") or self.name.endswith(".json"),
        }


class JobStore:
    """Database-backed repository for status tracking and generated artifacts."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """Initialize the job store."""
        self._session_factory = session_factory

    @contextmanager
    def _session(self) -> Iterator[Session]:
        """Yield a transactional SQLAlchemy session."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_job(
        self,
        *,
        job_id: str,
        input_filename: str,
        input_content_type: str | None,
        input_path: str,
        output_dir: str,
        pipeline_config: dict[str, object],
        expires_at: datetime,
    ) -> None:
        """Create a queued job record."""
        now = utc_now()
        with self._session() as session:
            session.add(
                JobEntity(
                    id=job_id,
                    status="queued",
                    input_filename=input_filename,
                    input_content_type=input_content_type,
                    input_path=input_path,
                    output_dir=output_dir,
                    pipeline_config=pipeline_config,
                    current_step=None,
                    error_message=None,
                    state_payload=None,
                    created_at=now,
                    updated_at=now,
                    expires_at=expires_at,
                )
            )

    def _require_job(self, session: Session, job_id: str) -> JobEntity:
        """Load a job or raise a descriptive error."""
        job = session.get(JobEntity, job_id)
        if job is None:
            raise KeyError(job_id)
        return job

    def get_job_input_record(self, job_id: str) -> DatabaseInputRecord:
        """Return the persisted input metadata for a pipeline job."""
        with self._session() as session:
            job = self._require_job(session, job_id)
            return DatabaseInputRecord(
                video_path=job.input_path,
                title=Path(job.input_filename).stem,
            )

    def has_pipeline_state(self, job_id: str) -> bool:
        """Return whether a pipeline state payload exists for the job."""
        with self._session() as session:
            job = self._require_job(session, job_id)
            return job.state_payload is not None

    def load_pipeline_state(self, job_id: str) -> dict[str, object] | None:
        """Load the serialized pipeline state payload for the job."""
        with self._session() as session:
            job = self._require_job(session, job_id)
            return job.state_payload

    def save_pipeline_state(self, job_id: str, payload: dict[str, object], current_step: str | None) -> None:
        """Persist the pipeline state payload and sync any artifact metadata."""
        now = utc_now()
        with self._session() as session:
            job = self._require_job(session, job_id)
            job.state_payload = payload
            job.current_step = current_step
            job.updated_at = now
            self._sync_artifacts_from_state(session, job_id, payload)

    def mark_current_step(self, job_id: str, step_name: str) -> None:
        """Persist the currently running step for status monitoring."""
        now = utc_now()
        with self._session() as session:
            job = self._require_job(session, job_id)
            if job.status == "queued":
                job.status = "running"
                job.started_at = now
            job.current_step = step_name
            job.updated_at = now

    def mark_running(self, job_id: str) -> None:
        """Mark a job as running."""
        now = utc_now()
        with self._session() as session:
            job = self._require_job(session, job_id)
            job.status = "running"
            job.started_at = job.started_at or now
            job.updated_at = now

    def mark_completed(self, job_id: str, current_step: str | None) -> None:
        """Mark a job as completed."""
        now = utc_now()
        with self._session() as session:
            job = self._require_job(session, job_id)
            job.status = "completed"
            job.current_step = current_step
            job.finished_at = now
            job.updated_at = now

    def mark_failed(self, job_id: str, message: str, current_step: str | None = None) -> None:
        """Mark a job as failed and store the error message."""
        now = utc_now()
        with self._session() as session:
            job = self._require_job(session, job_id)
            job.status = "failed"
            job.error_message = message
            job.current_step = current_step or job.current_step
            job.finished_at = now
            job.updated_at = now

    def record_artifact(self, job_id: str, name: str, path: str, kind: str) -> None:
        """Insert or update a generated artifact entry."""
        with self._session() as session:
            self._upsert_artifact(session, job_id, name=name, path=path, kind=kind)
            job = self._require_job(session, job_id)
            job.updated_at = utc_now()

    def _sync_artifacts_from_state(self, session: Session, job_id: str, payload: dict[str, object]) -> None:
        """Mirror pipeline state artifact entries into the database."""
        raw_artifacts = payload.get("artifacts")
        if not isinstance(raw_artifacts, dict):
            return
        items = raw_artifacts.get("items", raw_artifacts)
        if not isinstance(items, dict):
            return
        for name, entry in items.items():
            if not isinstance(entry, dict):
                continue
            path = str(entry.get("path") or "").strip()
            kind = str(entry.get("kind") or "file").strip()
            if path:
                self._upsert_artifact(session, job_id, name=str(name), path=path, kind=kind)

    def _upsert_artifact(self, session: Session, job_id: str, *, name: str, path: str, kind: str) -> None:
        """Insert or update an artifact row for the given job/name."""
        artifact = session.scalar(
            select(ArtifactEntity).where(ArtifactEntity.job_id == job_id, ArtifactEntity.name == name)
        )
        file_path = Path(path)
        media_type = mimetypes.guess_type(path)[0]
        size_bytes = file_path.stat().st_size if file_path.exists() else None
        if artifact is None:
            artifact = ArtifactEntity(
                job_id=job_id,
                name=name,
                path=path,
                kind=kind,
                media_type=media_type,
                size_bytes=size_bytes,
                created_at=utc_now(),
            )
            session.add(artifact)
            return
        artifact.path = path
        artifact.kind = kind
        artifact.media_type = media_type
        artifact.size_bytes = size_bytes

    def get_job_payload(self, job_id: str) -> dict[str, Any]:
        """Return a serialized API payload for a job."""
        with self._session() as session:
            job = self._require_job(session, job_id)
            return self._serialize_job(job)

    def list_artifacts(self, job_id: str) -> list[ArtifactSnapshot]:
        """List serialized artifacts for a job."""
        with self._session() as session:
            job = self._require_job(session, job_id)
            return [self._artifact_snapshot(item) for item in job.artifacts]

    def get_artifact_snapshot(self, job_id: str, artifact_name: str) -> ArtifactSnapshot:
        """Return one artifact row by job id and artifact name."""
        with self._session() as session:
            artifact = session.scalar(
                select(ArtifactEntity).where(
                    ArtifactEntity.job_id == job_id,
                    ArtifactEntity.name == artifact_name,
                )
            )
            if artifact is None:
                raise KeyError(artifact_name)
            return self._artifact_snapshot(artifact)

    def cleanup_expired_jobs(self, now: datetime | None = None) -> list[str]:
        """Delete expired jobs and their managed storage trees."""
        effective_now = now or utc_now()
        removed_roots: list[Path] = []
        removed_ids: list[str] = []
        with self._session() as session:
            jobs = list(
                session.scalars(
                    select(JobEntity).where(
                        JobEntity.expires_at.is_not(None),
                        JobEntity.expires_at <= effective_now,
                    )
                )
            )
            for job in jobs:
                removed_ids.append(job.id)
                removed_roots.append(Path(job.output_dir).parent)
                session.delete(job)
        for root in removed_roots:
            shutil.rmtree(root, ignore_errors=True)
        return removed_ids

    def _artifact_snapshot(self, artifact: ArtifactEntity) -> ArtifactSnapshot:
        """Convert an ORM artifact row into a serializable snapshot."""
        return ArtifactSnapshot(
            name=artifact.name,
            kind=artifact.kind,
            path=artifact.path,
            media_type=artifact.media_type,
            size_bytes=artifact.size_bytes,
            created_at=artifact.created_at,
            exists=Path(artifact.path).exists(),
        )

    def _serialize_job(self, job: JobEntity) -> dict[str, Any]:
        """Convert an ORM job row into the API response payload."""
        return {
            "job_id": job.id,
            "status": job.status,
            "input_filename": job.input_filename,
            "input_content_type": job.input_content_type,
            "current_step": job.current_step,
            "error_message": job.error_message,
            "pipeline_config": job.pipeline_config,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "expires_at": job.expires_at,
            "artifacts": [self._artifact_snapshot(item).to_dict(job.id) for item in job.artifacts],
        }
