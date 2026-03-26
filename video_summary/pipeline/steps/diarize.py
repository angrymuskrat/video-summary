"""Pipeline step implementation for diarize."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext


class DiarizeStep:
    """Pipeline step that handles diarize."""
    name = "diarize"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        if not context.config.hf_token:
            raise RuntimeError("Hugging Face token is required for diarization (`--hf-token` or `HF_TOKEN`).")
        prepared_media = context.require_prepared_media()
        context.state.speaker_turns = context.diarization_engine.diarize(prepared_media.audio_path, context.config)
