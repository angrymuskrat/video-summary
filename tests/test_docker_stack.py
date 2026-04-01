"""Static checks for Docker stack GPU readiness."""


from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_api_dockerfile_uses_cuda_runtime_and_cuda_torch_wheels() -> None:
    """The API image should provide CUDA runtime libraries for torch and pyannote."""
    dockerfile = _read("docker/api/Dockerfile")

    assert "FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04" in dockerfile
    assert 'ENV VIRTUAL_ENV=/opt/venv' in dockerfile
    assert 'RUN python3 -m venv "$VIRTUAL_ENV"' in dockerfile
    assert '"$VIRTUAL_ENV/bin/python" -m pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128' in dockerfile
    assert 'CMD ["python", "-m", "uvicorn", "video_summary.webapp.app:app"' in dockerfile


def test_compose_api_service_requests_gpu_access() -> None:
    """The API service should request GPU access from Docker Compose."""
    compose = _read("docker-compose.yml")

    assert "  api:" in compose
    assert "    gpus: all" in compose
    assert "      NVIDIA_VISIBLE_DEVICES: all" in compose
    assert "      NVIDIA_DRIVER_CAPABILITIES: compute,utility,video" in compose
