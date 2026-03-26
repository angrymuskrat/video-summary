"""OpenAI-backed transcript summarization for the video summary pipeline."""


from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib import error, request

from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, SummaryResult, Utterance


def _extract_output_text(payload: dict[str, Any]) -> str:
    """Extract the aggregated text payload from a Responses API response."""
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    lines: list[str] = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            text_value = content.get("text")
            if isinstance(text_value, str) and text_value.strip():
                lines.append(text_value.strip())
    return "\n".join(lines).strip()


def _extract_json_block(text: str) -> dict[str, Any]:
    """Parse the first JSON object found in model text output."""
    text = text.strip()
    if not text:
        raise ValueError("OpenAI summarizer returned empty output.")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def _build_transcript(utterances: list[Utterance]) -> str:
    """Render transcript-only input for the model prompt."""
    lines = [f"Speaker {item.speaker}: {item.text.strip()}" for item in utterances if item.text.strip()]
    return "\n".join(lines).strip()


def _trim_list(value: Any) -> list[str]:
    """Normalize a model-produced array of strings."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


@dataclass(frozen=True)
class OpenAIRequest:
    """Transport payload for a single summary request."""

    api_key: str
    model: str
    base_url: str
    timeout_sec: float
    transcript: str
    title_hint: str


def _default_transport(payload: OpenAIRequest) -> str:
    """Send a summary request to the OpenAI Responses API."""
    developer_prompt = (
        "You summarize meeting transcripts. Ignore slides and any other modality. "
        "Return strict JSON with keys title, overview, bullet_points, action_items. "
        "bullet_points and action_items must be arrays of short strings."
    )
    body = {
        "model": payload.model,
        "input": [
            {
                "role": "developer",
                "content": [{"type": "input_text", "text": developer_prompt}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Meeting title hint: {payload.title_hint}\n"
                            "Summarize the following transcript only.\n\n"
                            f"{payload.transcript}"
                        ),
                    }
                ],
            },
        ],
    }
    raw_request = request.Request(
        url=f"{payload.base_url.rstrip('/')}/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {payload.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(raw_request, timeout=payload.timeout_sec) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI summarization request failed with HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"OpenAI summarization request failed: {exc.reason}") from exc
    return _extract_output_text(response_payload)


class OpenAISummarizer:
    """Summarizer that delegates transcript summarization to an OpenAI-compatible API."""

    def __init__(self, transport: Callable[[OpenAIRequest], str] | None = None) -> None:
        """Initialize the OpenAI summarizer."""
        self._transport = transport or _default_transport

    def summarize(
        self,
        utterances: list[Utterance],
        slides: list[SceneSegment],
        config: PipelineConfig,
    ) -> SummaryResult:
        """Summarize transcript content using OpenAI-compatible server settings."""
        del slides
        transcript = _build_transcript(utterances)
        if not transcript:
            return SummaryResult(
                title=f"Meeting summary for {config.input_path.stem}",
                overview="Transcript is empty, so no LLM summary was generated.",
            )
        if not config.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when summarizer_provider='openai'.")
        model = config.openai_model or "gpt-5-nano"
        response_text = self._transport(
            OpenAIRequest(
                api_key=config.openai_api_key,
                model=model,
                base_url=config.openai_base_url or "https://api.openai.com/v1",
                timeout_sec=config.openai_timeout_sec,
                transcript=transcript,
                title_hint=config.input_path.stem,
            )
        )
        payload = _extract_json_block(response_text)
        return SummaryResult(
            title=str(payload.get("title") or f"Meeting summary for {config.input_path.stem}").strip(),
            overview=str(payload.get("overview") or "").strip(),
            bullet_points=_trim_list(payload.get("bullet_points")),
            action_items=_trim_list(payload.get("action_items")),
        )
