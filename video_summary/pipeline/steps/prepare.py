"""Pipeline step implementation for prepare."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class PrepareStep:
    """Pipeline step that handles prepare."""
    name = "prepare"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        source = context.input_reader.load(context.config)
        context.state.input_source = source
        context.state.prepared_media = context.media_preparator.prepare(source, context.config)
