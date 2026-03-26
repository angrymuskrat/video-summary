"""Environment-driven settings for the video-summary web application."""


from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings for the API, storage, retention, and OpenAI integration."""

    database_url: str
    storage_root: Path
    artifact_retention_hours: int = 24 * 7
    cleanup_interval_seconds: int = 60 * 30
    openai_api_key: str | None = None
    openai_model: str | None = "gpt-5-nano"
    openai_base_url: str | None = None
    openai_timeout_sec: float = 60.0
    frontend_origin: str | None = None
    cleanup_on_request: bool = True

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Load settings from process environment."""
        storage_root = Path(os.environ.get("VIDEO_SUMMARY_STORAGE_ROOT", "./data")).expanduser()
        return cls(
            database_url=os.environ.get("VIDEO_SUMMARY_DATABASE_URL", "sqlite+pysqlite:///./video-summary.db"),
            storage_root=storage_root.resolve(),
            artifact_retention_hours=int(os.environ.get("VIDEO_SUMMARY_ARTIFACT_RETENTION_HOURS", 24 * 7)),
            cleanup_interval_seconds=int(os.environ.get("VIDEO_SUMMARY_CLEANUP_INTERVAL_SECONDS", 60 * 30)),
            openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
            openai_model=os.environ.get("OPENAI_MODEL", "gpt-5-nano") or None,
            openai_base_url=os.environ.get("OPENAI_BASE_URL") or None,
            openai_timeout_sec=float(os.environ.get("OPENAI_TIMEOUT_SEC", 60.0)),
            frontend_origin=os.environ.get("VIDEO_SUMMARY_FRONTEND_ORIGIN") or None,
            cleanup_on_request=_env_bool("VIDEO_SUMMARY_CLEANUP_ON_REQUEST", True),
        )
