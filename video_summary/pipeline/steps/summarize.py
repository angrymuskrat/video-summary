from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class SummarizeStep:
    name = "summarize"

    def run(self, context: PipelineContext) -> None:
        alignment = context.require_alignment()
        context.state.summary = context.summarizer.summarize(
            alignment.utterances,
            context.state.slide_segments,
            context.config,
        )
