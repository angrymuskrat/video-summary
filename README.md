# Video Summary

`video-summary` is a local library for processing meeting recordings into transcripts, summaries, subtitles, and presentation artifacts.

The repository is organized around a small core package with pluggable interfaces and concrete adapters for media preparation, ASR, diarization, scene detection, subtitle generation, presentation export, and artifact persistence.

## Entry Points

- `python -m video_summary` runs the package CLI through [`video_summary.main`](./video_summary/main.py).
- `video_summary.main:main` is exposed as the `video-summary` console script in `pyproject.toml`.
- [`meeting_pipeline.py`](./meeting_pipeline.py) is a compatibility wrapper that forwards legacy CLI usage to the package entrypoint.

## Repository Layout

```text
video_summary/
  __init__.py
  cli.py
  config.py
  main.py
  orchestrator.py
  adapters/
  domain/
  interfaces/
  pipeline/
  services/
tests/
meeting_pipeline.py
```

Key sections:

- [`video_summary/`](./video_summary/README.md) contains package exports, CLI helpers, configuration, and orchestration code.
- [`video_summary/adapters/`](./video_summary/adapters/README.md) contains concrete backend integrations.
- [`video_summary/domain/`](./video_summary/domain/README.md) contains shared dataclasses and pipeline state models.
- [`video_summary/interfaces/`](./video_summary/interfaces/README.md) contains protocols for pluggable components.
- [`video_summary/pipeline/`](./video_summary/pipeline/README.md) contains the runtime context and step implementations.
- [`video_summary/services/`](./video_summary/services/README.md) contains pure helper services.
- [`tests/`](./tests/README.md) contains unit tests built around fakes and lightweight filesystem assertions.

## CLI Example

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
  --output-dir C:\path\to\out
```

## Python API

```python
from video_summary.config import PipelineConfig
from video_summary.orchestrator import build_default_pipeline

config = PipelineConfig.from_paths(
    input_path="meeting.webm",
    output_dir="out",
    hf_token="hf_xxx",
)

pipeline = build_default_pipeline(config)
state = pipeline.run()
```

## Testing

The test suite is designed around fakes and mock-like adapters, so it does not require real ASR, diarization, scene detection, or PPTX generation services to validate orchestration and filesystem behavior.

Run:

```powershell
pytest -q
```

## Notes

- The default runtime adapters still target `ffmpeg`, `faster-whisper`, `pyannote.audio`, `scenedetect`, and `python-pptx`.
- Filesystem-backed reader, writer, and state store adapters are implemented and covered by tests.
- Database-backed reader, writer, and state store adapters are placeholder extension points, so storage can evolve without changing the orchestrator API.
