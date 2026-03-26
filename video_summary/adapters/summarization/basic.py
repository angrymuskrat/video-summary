from __future__ import annotations

from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, SummaryResult, Utterance


def _trim(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


class BasicSummarizer:
    def summarize(
        self,
        utterances: list[Utterance],
        slides: list[SceneSegment],
        config: PipelineConfig,
    ) -> SummaryResult:
        speakers = sorted({utterance.speaker for utterance in utterances})
        overview = (
            f"Processed {len(utterances)} utterances from {len(speakers) or 0} speakers, "
            f"with {len(slides)} slide segments detected."
        )

        highlights = [_trim(utterance.text) for utterance in utterances[:5] if utterance.text.strip()]
        action_markers = (
            "todo",
            "action",
            "next",
            "follow up",
            "follow-up",
            "need",
            "needs",
            "should",
            "нужно",
            "надо",
            "сделать",
            "договорились",
        )
        action_items = [
            _trim(utterance.text)
            for utterance in utterances
            if any(marker in utterance.text.casefold() for marker in action_markers)
        ][:5]

        if not highlights and utterances:
            highlights = [_trim(utterance.text) for utterance in utterances[:3]]

        return SummaryResult(
            title=f"Meeting summary for {config.input_path.stem}",
            overview=overview,
            bullet_points=highlights,
            action_items=action_items,
        )
