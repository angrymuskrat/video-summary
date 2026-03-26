"""Application services for upload handling, async job execution, and cleanup."""


from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Callable
from uuid import uuid4

from fastapi import UploadFile

from video_summary.adapters.readers import DatabaseInputReader
from video_summary.adapters.state_store import DatabaseStateStore
from video_summary.adapters.writers import DatabaseArtifactWriter
from video_summary.config import STEP_ORDER, PipelineConfig
from video_summary.orchestrator import build_default_pipeline
from video_summary.webapp.repository import JobStore, utc_now
from video_summary.webapp.settings import AppSettings


def _clean_text(value: str | None) -> str | None:
    """Trim a text value and normalize blanks to None."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@dataclass(frozen=True)
class JobSubmission:
    """User-supplied pipeline parameters accepted by the web application."""

    hf_token: str | None = None
    language: str | None = None
    model: str = "large-v3"
    device: str = "cuda"
    compute_type: str = "float16"
    ffmpeg_video_encoder: str = "auto"
    presentation: str = "auto"
    scene_detector: str = "content"
    scene_threshold: float | None = None
    min_scene_sec: float = 5.0
    num_speakers: int | None = None
    min_speakers: int | None = None
    max_speakers: int | None = None
    subtitle_max_chars: int = 84
    subtitle_max_duration: float = 4.5
    transcript_gap: float = 0.8
    start_from: str = "prepare"
    export_pdf: bool = False
    keep_work_files: bool = False
    summarizer_provider: str = "basic"

    def to_public_config(self) -> dict[str, object]:
        """Return a sanitized config snapshot safe to store and expose."""
        return {
            "language": self.language,
            "model": self.model,
            "device": self.device,
            "compute_type": self.compute_type,
            "ffmpeg_video_encoder": self.ffmpeg_video_encoder,
            "presentation": self.presentation,
            "scene_detector": self.scene_detector,
            "scene_threshold": self.scene_threshold,
            "min_scene_sec": self.min_scene_sec,
            "num_speakers": self.num_speakers,
            "min_speakers": self.min_speakers,
            "max_speakers": self.max_speakers,
            "subtitle_max_chars": self.subtitle_max_chars,
            "subtitle_max_duration": self.subtitle_max_duration,
            "transcript_gap": self.transcript_gap,
            "start_from": self.start_from,
            "export_pdf": self.export_pdf,
            "keep_work_files": self.keep_work_files,
            "summarizer_provider": self.summarizer_provider,
            "hf_token_provided": bool(self.hf_token),
        }

    def to_pipeline_config(self, *, input_path: Path, output_dir: Path, settings: AppSettings) -> PipelineConfig:
        """Translate the web request into the core pipeline configuration object."""
        return PipelineConfig.from_paths(
            str(input_path),
            str(output_dir),
            hf_token=self.hf_token,
            language=self.language,
            model=self.model,
            device=self.device,
            compute_type=self.compute_type,
            ffmpeg_video_encoder=self.ffmpeg_video_encoder,
            presentation=self.presentation,
            scene_detector=self.scene_detector,
            scene_threshold=self.scene_threshold,
            min_scene_sec=self.min_scene_sec,
            num_speakers=self.num_speakers,
            min_speakers=self.min_speakers,
            max_speakers=self.max_speakers,
            subtitle_max_chars=self.subtitle_max_chars,
            subtitle_max_duration=self.subtitle_max_duration,
            transcript_gap=self.transcript_gap,
            start_from=self.start_from,
            export_pdf=self.export_pdf,
            keep_work_files=self.keep_work_files,
            summarizer_provider=self.summarizer_provider,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            openai_base_url=settings.openai_base_url,
            openai_timeout_sec=settings.openai_timeout_sec,
        )

    @classmethod
    def from_form(
        cls,
        *,
        hf_token: str | None = None,
        language: str | None = None,
        model: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
        ffmpeg_video_encoder: str = "auto",
        presentation: str = "auto",
        scene_detector: str = "content",
        scene_threshold: float | None = None,
        min_scene_sec: float = 5.0,
        num_speakers: int | None = None,
        min_speakers: int | None = None,
        max_speakers: int | None = None,
        subtitle_max_chars: int = 84,
        subtitle_max_duration: float = 4.5,
        transcript_gap: float = 0.8,
        start_from: str = "prepare",
        export_pdf: bool = False,
        keep_work_files: bool = False,
        summarizer_provider: str = "basic",
    ) -> "JobSubmission":
        """Build a validated submission from HTML form fields."""
        return cls(
            hf_token=_clean_text(hf_token),
            language=_clean_text(language),
            model=model.strip() or "large-v3",
            device=device,
            compute_type=compute_type.strip() or "float16",
            ffmpeg_video_encoder=ffmpeg_video_encoder,
            presentation=presentation,
            scene_detector=scene_detector,
            scene_threshold=scene_threshold,
            min_scene_sec=min_scene_sec,
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            subtitle_max_chars=subtitle_max_chars,
            subtitle_max_duration=subtitle_max_duration,
            transcript_gap=transcript_gap,
            start_from=start_from,
            export_pdf=export_pdf,
            keep_work_files=keep_work_files,
            summarizer_provider=summarizer_provider,
        )


PIPELINE_FORM_SCHEMA = [
    {"name": "hf_token", "label": "Hugging Face Token", "kind": "password", "default": "", "help": "Optional token for pyannote diarization."},
    {"name": "language", "label": "Language", "kind": "text", "default": "", "placeholder": "ru or en"},
    {"name": "model", "label": "ASR Model", "kind": "text", "default": "large-v3"},
    {"name": "device", "label": "Device", "kind": "select", "default": "cuda", "options": ["cuda", "cpu"]},
    {"name": "compute_type", "label": "Compute Type", "kind": "text", "default": "float16"},
    {
        "name": "ffmpeg_video_encoder",
        "label": "FFmpeg Video Encoder",
        "kind": "select",
        "default": "auto",
        "options": ["auto", "h264_nvenc", "libx264"],
    },
    {"name": "presentation", "label": "Presentation", "kind": "select", "default": "auto", "options": ["auto", "yes", "no"]},
    {
        "name": "scene_detector",
        "label": "Scene Detector",
        "kind": "select",
        "default": "content",
        "options": ["content", "adaptive", "hash"],
    },
    {"name": "scene_threshold", "label": "Scene Threshold", "kind": "number", "default": "", "step": "0.1"},
    {"name": "min_scene_sec", "label": "Min Scene Seconds", "kind": "number", "default": 5.0, "step": "0.1"},
    {"name": "num_speakers", "label": "Exact Speakers", "kind": "number", "default": "", "step": "1"},
    {"name": "min_speakers", "label": "Min Speakers", "kind": "number", "default": "", "step": "1"},
    {"name": "max_speakers", "label": "Max Speakers", "kind": "number", "default": "", "step": "1"},
    {"name": "subtitle_max_chars", "label": "Subtitle Max Chars", "kind": "number", "default": 84, "step": "1"},
    {"name": "subtitle_max_duration", "label": "Subtitle Max Duration", "kind": "number", "default": 4.5, "step": "0.1"},
    {"name": "transcript_gap", "label": "Transcript Gap", "kind": "number", "default": 0.8, "step": "0.1"},
    {"name": "start_from", "label": "Start From Step", "kind": "select", "default": "prepare", "options": list(STEP_ORDER)},
    {"name": "summarizer_provider", "label": "Summarizer", "kind": "select", "default": "basic", "options": ["basic", "openai"]},
    {"name": "export_pdf", "label": "Export PDF", "kind": "checkbox", "default": False},
    {"name": "keep_work_files", "label": "Keep Work Files", "kind": "checkbox", "default": False},
]


class JobService:
    """High-level orchestration around uploads, job execution, and cleanup."""

    def __init__(
        self,
        *,
        settings: AppSettings,
        store: JobStore,
        pipeline_factory: Callable[..., object] = build_default_pipeline,
    ) -> None:
        """Initialize the job service."""
        self._settings = settings
        self._store = store
        self._pipeline_factory = pipeline_factory
        self._cleanup_lock = Lock()
        self._last_cleanup = utc_now() - timedelta(seconds=settings.cleanup_interval_seconds)

    @property
    def settings_payload(self) -> dict[str, object]:
        """Return public settings and frontend form metadata."""
        return {
            "fields": PIPELINE_FORM_SCHEMA,
            "retention_hours": self._settings.artifact_retention_hours,
            "openai_summary_available": bool(self._settings.openai_api_key and self._settings.openai_model),
        }

    async def create_job(self, *, upload: UploadFile, submission: JobSubmission) -> dict[str, Any]:
        """Persist an uploaded file, create a queued job, and start async processing."""
        await self.cleanup_if_due()
        job_id = uuid4().hex
        job_root = self._settings.storage_root / "jobs" / job_id
        input_dir = job_root / "input"
        output_dir = job_root / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(upload.filename or "upload.bin").name
        input_path = input_dir / filename
        with input_path.open("wb") as handle:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
        await upload.close()

        self._store.create_job(
            job_id=job_id,
            input_filename=filename,
            input_content_type=upload.content_type,
            input_path=str(input_path),
            output_dir=str(output_dir),
            pipeline_config=submission.to_public_config(),
            expires_at=utc_now() + timedelta(hours=self._settings.artifact_retention_hours),
        )

        worker = Thread(
            target=self._run_job,
            args=(job_id, submission, input_path, output_dir),
            daemon=True,
            name=f"video-summary-job-{job_id}",
        )
        worker.start()
        return self._store.get_job_payload(job_id)

    def _run_job(self, job_id: str, submission: JobSubmission, input_path: Path, output_dir: Path) -> None:
        """Execute the pipeline in a background thread and persist job status updates."""
        config = submission.to_pipeline_config(
            input_path=input_path,
            output_dir=output_dir,
            settings=self._settings,
        )
        self._store.mark_running(job_id)
        try:
            pipeline = self._pipeline_factory(
                config,
                input_reader=DatabaseInputReader(self._store, job_id),
                artifact_writer=DatabaseArtifactWriter(config, self._store, job_id),
                state_store=DatabaseStateStore(self._store, job_id),
            )
            state = pipeline.run()
        except Exception as exc:
            self._store.mark_failed(job_id, str(exc))
            return
        self._store.mark_completed(job_id, state.start_from)

    async def cleanup_if_due(self) -> list[str]:
        """Run retention cleanup when the configured interval has elapsed."""
        if not self._settings.cleanup_on_request:
            return []
        now = utc_now()
        if (now - self._last_cleanup).total_seconds() < self._settings.cleanup_interval_seconds:
            return []
        with self._cleanup_lock:
            now = utc_now()
            if (now - self._last_cleanup).total_seconds() < self._settings.cleanup_interval_seconds:
                return []
            removed = self._store.cleanup_expired_jobs(now)
            self._last_cleanup = now
            return removed

    async def job_status(self, job_id: str) -> dict[str, Any]:
        """Return the latest status payload for a job."""
        await self.cleanup_if_due()
        return self._store.get_job_payload(job_id)

    async def artifacts(self, job_id: str) -> dict[str, Any]:
        """Return the job payload including generated artifact metadata."""
        await self.cleanup_if_due()
        payload = self._store.get_job_payload(job_id)
        payload["artifacts"] = [item.to_dict(job_id) for item in self._store.list_artifacts(job_id)]
        return payload

    async def artifact_file(self, job_id: str, artifact_name: str) -> Path:
        """Resolve the on-disk file path for one artifact."""
        await self.cleanup_if_due()
        artifact = self._store.get_artifact_snapshot(job_id, artifact_name)
        path = Path(artifact.path)
        if not path.exists():
            raise FileNotFoundError(path)
        return path
