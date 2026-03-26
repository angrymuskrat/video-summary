"""Pipeline step implementation for summarize."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class SummarizeStep:
    """Pipeline step that handles summarize."""
    name = "summarize"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        alignment = context.require_alignment()
        context.state.summary = context.summarizer.summarize(
            alignment.utterances,
            context.state.slide_segments,
            context.config,
        )
