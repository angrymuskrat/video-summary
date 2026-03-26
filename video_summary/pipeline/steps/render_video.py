"""Pipeline step implementation for render video."""


from __future__ import annotations

from pathlib import Path

from video_summary.pipeline.context import PipelineContext


class RenderVideoStep:
    """Pipeline step that handles render video."""
    name = "render"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        layout = context.config.layout()
        if not layout.subtitles_srt.exists() or not layout.subtitles_ass.exists():
            raise FileNotFoundError("Subtitle files are missing. Run or restore the 'write' step first.")
        prepared_media = context.require_prepared_media()
        context.register_artifacts(context.video_renderer.render(prepared_media, context.config))
