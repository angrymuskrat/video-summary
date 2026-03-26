"""Pipeline step implementation for transcribe."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class TranscribeStep:
    """Pipeline step that handles transcribe."""
    name = "asr"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        prepared_media = context.require_prepared_media()
        words, meta = context.asr_engine.transcribe(prepared_media.audio_path, context.config)
        context.state.asr_words = words
        context.state.asr_meta = meta
