"""SQLAlchemy ORM models for jobs and generated artifacts."""


from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    """Base declarative model for the web application schema."""


class JobEntity(Base):
    """Pipeline job persisted for web/API status tracking."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    input_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    input_content_type: Mapped[str | None] = mapped_column(String(255))
    input_path: Mapped[str] = mapped_column(Text, nullable=False)
    output_dir: Mapped[str] = mapped_column(Text, nullable=False)
    current_step: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    pipeline_config: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    state_payload: Mapped[dict[str, object] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    artifacts: Mapped[list["ArtifactEntity"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="ArtifactEntity.name",
    )


class ArtifactEntity(Base):
    """Generated artifact metadata persisted per job."""

    __tablename__ = "artifacts"
    __table_args__ = (UniqueConstraint("job_id", "name", name="uq_artifacts_job_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    media_type: Mapped[str | None] = mapped_column(String(255))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    job: Mapped[JobEntity] = relationship(back_populates="artifacts")
