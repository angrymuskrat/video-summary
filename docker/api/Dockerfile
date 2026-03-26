FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md requirements.txt ./
COPY video_summary ./video_summary
COPY meeting_pipeline.py ./

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "video_summary.webapp.app:app", "--host", "0.0.0.0", "--port", "8000"]
