"""Pipeline step implementation for align."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class AlignStep:
    """Pipeline step that handles align."""
    name = "align"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        context.state.alignment = context.alignment_engine.align(
            context.state.asr_words,
            context.state.speaker_turns,
            context.config,
        )
