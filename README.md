# Video Summary Library

`meeting_pipeline.py` is now a thin compatibility wrapper around the `video_summary` package.

The repository provides a small library for processing online meeting recordings with modular, replaceable components for:
- input reading
- media preparation
- speech-to-text
- diarization / speaker attribution
- alignment and transcript assembly
- scene detection
- slide binding
- summarization
- subtitle generation
- presentation generation
- artifact writing
- state persistence

## Layout

```text
video_summary/
  cli.py
  config.py
  main.py
  orchestrator.py
  domain/
  interfaces/
  adapters/
  pipeline/
  services/
tests/
meeting_pipeline.py
```

Key entrypoints:
- `video_summary.main:main` for the library CLI
- `python -m video_summary ...` for module execution
- `meeting_pipeline.py` for the legacy-compatible wrapper

## CLI

Legacy usage is preserved:

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

Unit tests are designed to use fakes and mocks instead of real ASR, diarization, scene detection, or PPTX generation backends.

Expected command:

```powershell
pytest -q
```

## Notes

- Filesystem-backed reader, writer, and state store adapters are included.
- Database-backed reader, writer, and state store adapters are present as extension-point placeholders so the orchestrator does not need to change when a DB backend is added later.
- The default runtime adapters still target `ffmpeg`, `faster-whisper`, `pyannote.audio`, `scenedetect`, and `python-pptx`.
