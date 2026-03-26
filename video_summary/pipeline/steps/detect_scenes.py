"""Pipeline step implementation for detect scenes."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class DetectScenesStep:
    """Pipeline step that handles detect scenes."""
    name = "scenes"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        prepared_media = context.require_prepared_media()
        context.state.scene_analysis = context.scene_detector.detect(
            prepared_media.video_path,
            prepared_media.metadata,
            context.config,
        )
