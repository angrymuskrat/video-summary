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


def _env_text(*names: str) -> str | None:
    """Read the first non-empty text environment variable from the provided names."""
    for name in names:
        raw = os.environ.get(name)
        if raw and raw.strip():
            return raw.strip()
    return None


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
            openai_api_key=_env_text("OPENAI_API_KEY"),
            openai_model=_env_text("OPENAI_MODEL", "VLLM_MODEL") or "gpt-5-nano",
            openai_base_url=_env_text("OPENAI_BASE_URL"),
            openai_timeout_sec=float(os.environ.get("OPENAI_TIMEOUT_SEC", 60.0)),
            frontend_origin=os.environ.get("VIDEO_SUMMARY_FRONTEND_ORIGIN") or None,
            cleanup_on_request=_env_bool("VIDEO_SUMMARY_CLEANUP_ON_REQUEST", True),
        )
