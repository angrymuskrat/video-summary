"""Pipeline step implementation for bind slides."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class BindSlidesStep:
    """Pipeline step that handles bind slides."""
    name = "slides"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        prepared_media = context.require_prepared_media()
        alignment = context.require_alignment()
        scene_analysis = context.require_scene_analysis()
        context.state.slide_segments = context.slide_binder.bind(
            scene_analysis,
            alignment.utterances,
            prepared_media,
            context.config,
        )
