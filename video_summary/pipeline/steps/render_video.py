from __future__ import annotations

from pathlib import Path

from video_summary.pipeline.context import PipelineContext


class RenderVideoStep:
    name = "render"

    def run(self, context: PipelineContext) -> None:
        layout = context.config.layout()
        if not layout.subtitles_srt.exists() or not layout.subtitles_ass.exists():
            raise FileNotFoundError("Subtitle files are missing. Run or restore the 'write' step first.")
        prepared_media = context.require_prepared_media()
        context.register_artifacts(context.video_renderer.render(prepared_media, context.config))
