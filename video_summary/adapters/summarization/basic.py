"""Concrete implementation of meeting summarization for the video summary pipeline."""


from __future__ import annotations

from video_summary.config import PipelineConfig
from video_summary.domain.models import SceneSegment, SummaryResult, Utterance


def _trim(text: str, limit: int = 120) -> str:
    """Trim.

    Args:
        text (str): Value for text.
        limit (int): Optional value for limit.

    Returns:
        str: Result produced by trim.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


class BasicSummarizer:
    """Basic summarizer."""

    def summarize(
        self,
        utterances: list[Utterance],
        slides: list[SceneSegment],
        config: PipelineConfig,
    ) -> SummaryResult:
        """Summarize the requested pipeline data.

        Args:
            utterances (list[Utterance]): Value for utterances.
            slides (list[SceneSegment]): Value for slides.
            config (PipelineConfig): Pipeline configuration to use for the operation.

        Returns:
            SummaryResult: Result produced by summarize.
        """
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
            "\u043d\u0443\u0436\u043d\u043e",
            "\u043d\u0430\u0434\u043e",
            "\u0441\u0434\u0435\u043b\u0430\u0442\u044c",
            "\u0434\u043e\u0433\u043e\u0432\u043e\u0440\u0438\u043b\u0438\u0441\u044c",
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
