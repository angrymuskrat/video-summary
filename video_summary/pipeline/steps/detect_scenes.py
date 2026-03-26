from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class DetectScenesStep:
    name = "scenes"

    def run(self, context: PipelineContext) -> None:
        prepared_media = context.require_prepared_media()
        context.state.scene_analysis = context.scene_detector.detect(
            prepared_media.video_path,
            prepared_media.metadata,
            context.config,
        )
