FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        ffmpeg \
        git \
        libgl1 \
        libglib2.0-0 \
        python3 \
        python3-pip \
        python3-venv \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv "$VIRTUAL_ENV"

COPY pyproject.toml README.md requirements.txt ./
COPY video_summary ./video_summary
COPY meeting_pipeline.py ./

RUN "$VIRTUAL_ENV/bin/python" -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN "$VIRTUAL_ENV/bin/python" -m pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN "$VIRTUAL_ENV/bin/python" -m pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "video_summary.webapp.app:app", "--host", "0.0.0.0", "--port", "8000"]
