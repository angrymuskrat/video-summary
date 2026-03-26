"""Pipeline step implementation for write outputs."""


from __future__ import annotations

from video_summary.pipeline.context import PipelineContext
from video_summary.services import render_transcript_text, transcript_payload


class WriteOutputsStep:
    """Pipeline step that handles write outputs."""
    name = "write"

    def run(self, context: PipelineContext) -> None:
        """Run the requested pipeline data.
        
        Args:
            context (PipelineContext): Value for context.
        """
        prepared_media = context.require_prepared_media()
        alignment = context.require_alignment()
        scene_analysis = context.require_scene_analysis()
        summary = context.require_summary()

        records = [
            context.artifact_writer.write_text(
                "transcript",
                render_transcript_text(alignment.utterances, include_roles=False, include_timestamps=True),
            ),
            context.artifact_writer.write_text(
                "transcript_with_roles",
                render_transcript_text(alignment.utterances, include_roles=True, include_timestamps=True),
            ),
            context.artifact_writer.write_text("summary", summary.to_markdown()),
        ]
        records.extend(context.subtitle_generator.generate(alignment.subtitles, prepared_media.metadata, context.config))
        records.extend(
            context.presentation_generator.generate(
                context.state.slide_segments,
                context.state.input_source.title if context.state.input_source and context.state.input_source.title else context.config.input_path.stem,
                context.config,
            )
        )
        context.register_artifacts(records)

        payload = transcript_payload(
            input_video=context.state.input_source.video_path if context.state.input_source else str(context.config.input_path),
            metadata=prepared_media.metadata,
            asr_meta=context.state.asr_meta,
            turns=context.state.speaker_turns,
            alignment=alignment,
            scene_analysis=scene_analysis,
            slide_segments=context.state.slide_segments,
            summary=summary,
            artifacts=context.state.artifacts,
        )
        transcript_record = context.artifact_writer.write_json("transcript_json", payload)
        context.register_artifacts([transcript_record])
        context.state.transcript_json = transcript_record.path
