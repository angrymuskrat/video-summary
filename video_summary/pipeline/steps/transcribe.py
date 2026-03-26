from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class TranscribeStep:
    name = "asr"

    def run(self, context: PipelineContext) -> None:
        prepared_media = context.require_prepared_media()
        words, meta = context.asr_engine.transcribe(prepared_media.audio_path, context.config)
        context.state.asr_words = words
        context.state.asr_meta = meta
