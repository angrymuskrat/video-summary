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

1. Open the main page.
2. Jump to the dedicated upload page.
3. Upload a file and submit the pipeline parameters.
4. Receive a job ID immediately.
5. Use the status page to monitor job state and timestamps.
6. Use the artifacts page to preview or download generated outputs by job ID.
7. Let the retention cleanup remove expired job rows and their managed files automatically.

## Server Settings

Environment variables used by the backend:

- `VIDEO_SUMMARY_DATABASE_URL`: SQLAlchemy connection string.
- `VIDEO_SUMMARY_STORAGE_ROOT`: root folder for uploaded files and generated artifacts.
- `VIDEO_SUMMARY_ARTIFACT_RETENTION_HOURS`: retention window for job/artifact records. Default: `168`.
- `VIDEO_SUMMARY_CLEANUP_INTERVAL_SECONDS`: cleanup cadence when request-driven cleanup is enabled.
- `VIDEO_SUMMARY_FRONTEND_ORIGIN`: optional CORS origin for a separately hosted frontend.
- `OPENAI_API_KEY`: enables the OpenAI-backed summarizer when `summarizer_provider=openai`.
- `OPENAI_MODEL`: model name for transcript summarization. If unset, the backend falls back to `VLLM_MODEL`.
- `OPENAI_BASE_URL`: optional OpenAI-compatible base URL.
- `OPENAI_TIMEOUT_SEC`: timeout for summary requests.
- `HF_TOKEN`: optional Hugging Face token for diarization.
- `VLLM_MODEL`: active local `vLLM` model name used by the compose stack and as the backend fallback model selector.

OpenAI credentials remain server-side only and are not exposed on the public form.

## Docker

Start the full stack:

```powershell
docker compose up --build
```

Start the stack with local `vLLM` summarization:

```powershell
docker compose --profile llm up --build
```

Default endpoints:

- Frontend: `http://localhost:8080`
- API health: `http://localhost:8080/api/health`
- `vLLM` OpenAI-compatible endpoint: `http://localhost:8000/v1`

The `api` container is GPU-ready: it is built on a CUDA 12.8 runtime image, installs CUDA-enabled PyTorch wheels, and requests `gpus: all` in `docker-compose.yml`. To actually run it on the GPU, the Docker host must have NVIDIA drivers plus NVIDIA Container Toolkit installed.

The compose stack includes:

- `frontend`: nginx serving the static UI and proxying `/api/*`
- `api`: FastAPI backend running the library pipeline
- `db`: PostgreSQL for job and artifact metadata
- `vllm`: optional GPU-backed OpenAI-compatible server for transcript summarization

The frontend nginx proxy is configured to accept upload bodies up to `2048M`, so large meeting recordings can reach the backend instead of failing with HTTP `413 Request Entity Too Large`.

Model downloads are stored in the bind-mounted directory configured by `VLLM_CACHE_DIR` and default to `docker/models/huggingface/`.

Copy `.env.example` to `.env` and choose the active preset by assigning `VLLM_MODEL` to one of:

- `VLLM_MODEL_16GB` for a 16 GB GPU
- `VLLM_MODEL_24GB` for a 24 GB GPU

The shipped example uses quantized Qwen instruct models as practical text summarization defaults:

- 16 GB preset: `Qwen/Qwen2.5-7B-Instruct-AWQ`
- 24 GB preset: `Qwen/Qwen2.5-14B-Instruct-AWQ`

## Frontend Pages

- `/main.html`: landing page with workflow overview and a button to the upload workspace
- `/upload.html`: upload form with all public pipeline controls
- `/index.html`: backward-compatible redirect to `/main.html`
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
