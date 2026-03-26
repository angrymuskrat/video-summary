from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class AlignStep:
    name = "align"

    def run(self, context: PipelineContext) -> None:
        context.state.alignment = context.alignment_engine.align(
            context.state.asr_words,
            context.state.speaker_turns,
            context.config,
        )
