# Video Summary

`video-summary` is a meeting-processing library plus a dockerized web wrapper with:

- a backend API for uploads, async job execution, status lookup, and artifact download
- a browser frontend with dedicated pages for upload, status, artifacts, and usage notes
- a database-backed application layer for job tracking and artifact retention cleanup
- optional OpenAI transcript-only summarization configured on the server

## Stack

- Core library: `video_summary/`
- Backend API: `video_summary/webapp/`
- Frontend pages: `frontend/`
- Docker assets: `docker/` and `docker-compose.yml`

## Web App Flow

1. Open the upload page.
2. Upload a file and submit the pipeline parameters.
3. Receive a job ID immediately.
4. Use the status page to monitor job state and timestamps.
5. Use the artifacts page to preview or download generated outputs by job ID.
6. Let the retention cleanup remove expired job rows and their managed files automatically.

## Server Settings

Environment variables used by the backend:

- `VIDEO_SUMMARY_DATABASE_URL`: SQLAlchemy connection string.
- `VIDEO_SUMMARY_STORAGE_ROOT`: root folder for uploaded files and generated artifacts.
- `VIDEO_SUMMARY_ARTIFACT_RETENTION_HOURS`: retention window for job/artifact records. Default: `168`.
- `VIDEO_SUMMARY_CLEANUP_INTERVAL_SECONDS`: cleanup cadence when request-driven cleanup is enabled.
- `VIDEO_SUMMARY_FRONTEND_ORIGIN`: optional CORS origin for a separately hosted frontend.
- `OPENAI_API_KEY`: enables the OpenAI-backed summarizer when `summarizer_provider=openai`.
- `OPENAI_MODEL`: model name for transcript summarization.
- `OPENAI_BASE_URL`: optional OpenAI-compatible base URL.
- `OPENAI_TIMEOUT_SEC`: timeout for summary requests.
- `HF_TOKEN`: optional Hugging Face token for diarization.

OpenAI credentials remain server-side only and are not exposed on the public form.

## Docker

Start the full stack:

```powershell
docker compose up --build
```

Default endpoints:

- Frontend: `http://localhost:8080`
- API health: `http://localhost:8080/api/health`

The compose stack includes:

- `frontend`: nginx serving the static UI and proxying `/api/*`
- `api`: FastAPI backend running the library pipeline
- `db`: PostgreSQL for job and artifact metadata

## Frontend Pages

- `/index.html`: upload form with all public pipeline controls
- `/status.html`: status lookup by job ID
- `/artifacts.html`: artifact browser by job ID
- `/help.html`: usage guide and runtime notes

## API Endpoints

- `GET /api/health`
- `GET /api/form-options`
- `POST /api/jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/artifacts`
- `GET /api/jobs/{job_id}/artifacts/{artifact_name}`

## Library Usage

Legacy-compatible wrapper:

```powershell
python meeting_pipeline.py `
  --input C:\path\to\meeting.webm `
  --output-dir C:\path\to\out `
  --hf-token YOUR_TOKEN `
  --language ru `
  --presentation auto `
  --ffmpeg-video-encoder auto `
  --export-pdf
```

Direct package entrypoint:

```powershell
python -m video_summary `
  --input C:\path\to\meeting.webm `
  --output-dir C:\path\to\out `
  --summarizer-provider basic
```

Python API:

```python
from video_summary.config import PipelineConfig
from video_summary.orchestrator import build_default_pipeline

config = PipelineConfig.from_paths(
    input_path="meeting.webm",
    output_dir="out",
    hf_token="hf_xxx",
    summarizer_provider="basic",
)

pipeline = build_default_pipeline(config)
state = pipeline.run()
```

## OpenAI Summarization

The OpenAI-backed summarizer:

- uses transcript utterances only
- ignores slides and other modalities
- is selected through `summarizer_provider="openai"`
- reads `OPENAI_API_KEY`, `OPENAI_MODEL`, and optional `OPENAI_BASE_URL`
- is tested with a stubbed transport and does not require live network calls in unit tests

## Testing

Run:

```powershell
pytest -q
```

Coverage includes:

- CLI/config mapping for the new summarizer selector
- OpenAI summarizer behavior with a stubbed transport
- web app upload -> job ID -> status -> artifacts flow
- retention cleanup for expired jobs and managed files
