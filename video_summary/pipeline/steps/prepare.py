from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class PrepareStep:
    name = "prepare"

    def run(self, context: PipelineContext) -> None:
        source = context.input_reader.load(context.config)
        context.state.input_source = source
        context.state.prepared_media = context.media_preparator.prepare(source, context.config)
