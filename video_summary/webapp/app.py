"""FastAPI application for uploads, status monitoring, and artifact browsing."""


from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Callable

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from video_summary.orchestrator import build_default_pipeline
from video_summary.webapp.database import create_session_factory, init_database
from video_summary.webapp.repository import JobStore
from video_summary.webapp.service import JobService, JobSubmission
from video_summary.webapp.settings import AppSettings


def _job_service(request: Request) -> JobService:
    """Return the shared job service from the FastAPI app state."""
    return request.app.state.job_service


def create_app(
    settings: AppSettings | None = None,
    *,
    pipeline_factory: Callable[..., object] = build_default_pipeline,
) -> FastAPI:
    """Create the FastAPI application instance."""
    resolved_settings = settings or AppSettings.from_env()
    session_factory = create_session_factory(resolved_settings.database_url)
    job_service = JobService(
        settings=resolved_settings,
        store=JobStore(session_factory),
        pipeline_factory=pipeline_factory,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        init_database(session_factory)
        resolved_settings.storage_root.mkdir(parents=True, exist_ok=True)
        yield

    app = FastAPI(title="video-summary webapp", version="0.1.0", lifespan=lifespan)
    app.state.settings = resolved_settings
    app.state.job_service = job_service
    app.state.session_factory = session_factory

    if resolved_settings.frontend_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[resolved_settings.frontend_origin],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/form-options")
    async def form_options(request: Request) -> dict[str, object]:
        return _job_service(request).settings_payload

    @app.post("/api/jobs", status_code=202)
    async def create_job_endpoint(
        request: Request,
        file: UploadFile = File(...),
        hf_token: str | None = Form(None),
        language: str | None = Form(None),
        model: str = Form("large-v3"),
        device: str = Form("cuda"),
        compute_type: str = Form("float16"),
        ffmpeg_video_encoder: str = Form("auto"),
        presentation: str = Form("auto"),
        scene_detector: str = Form("content"),
        scene_threshold: float | None = Form(None),
        min_scene_sec: float = Form(5.0),
        num_speakers: int | None = Form(None),
        min_speakers: int | None = Form(None),
        max_speakers: int | None = Form(None),
        subtitle_max_chars: int = Form(84),
        subtitle_max_duration: float = Form(4.5),
        transcript_gap: float = Form(0.8),
        start_from: str = Form("prepare"),
        export_pdf: bool = Form(False),
        keep_work_files: bool = Form(False),
        summarizer_provider: str = Form("basic"),
    ) -> dict[str, Any]:
        submission = JobSubmission.from_form(
            hf_token=hf_token,
            language=language,
            model=model,
            device=device,
            compute_type=compute_type,
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
        return await _job_service(request).create_job(upload=file, submission=submission)

    @app.get("/api/jobs/{job_id}")
    async def job_status(request: Request, job_id: str) -> dict[str, Any]:
        try:
            return await _job_service(request).job_status(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' was not found.") from exc

    @app.get("/api/jobs/{job_id}/artifacts")
    async def list_artifacts(request: Request, job_id: str) -> dict[str, Any]:
        try:
            return await _job_service(request).artifacts(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' was not found.") from exc

    @app.get("/api/jobs/{job_id}/artifacts/{artifact_name}")
    async def download_artifact(
        request: Request,
        job_id: str,
        artifact_name: str,
        download: bool = Query(False),
    ) -> FileResponse:
        try:
            artifact_path = await _job_service(request).artifact_file(job_id, artifact_name)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Artifact '{artifact_name}' was not found.") from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=f"Artifact file is missing: {exc}") from exc
        return FileResponse(
            path=artifact_path,
            filename=artifact_path.name if download else None,
            media_type=None,
        )

    return app


app = create_app()


def run() -> None:
    """Start the API server using the current environment settings."""
    uvicorn.run("video_summary.webapp.app:app", host="0.0.0.0", port=8000, reload=False)
