from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class BindSlidesStep:
    name = "slides"

    def run(self, context: PipelineContext) -> None:
        prepared_media = context.require_prepared_media()
        alignment = context.require_alignment()
        scene_analysis = context.require_scene_analysis()
        context.state.slide_segments = context.slide_binder.bind(
            scene_analysis,
            alignment.utterances,
            prepared_media,
            context.config,
        )
