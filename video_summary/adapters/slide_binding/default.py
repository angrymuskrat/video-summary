from __future__ import annotations

from pathlib import Path

from video_summary.adapters.media.ffmpeg import extract_frame
from video_summary.config import PipelineConfig
from video_summary.domain.models import PreparedMedia, SceneAnalysis, SceneSegment, Utterance
from video_summary.services import build_slide_segments


class DefaultSlideBinder:
    def bind(
        self,
        scene_analysis: SceneAnalysis,
        utterances: list[Utterance],
        prepared_media: PreparedMedia,
        config: PipelineConfig,
    ) -> list[SceneSegment]:
        layout = config.layout()
        layout.frames_dir.mkdir(parents=True, exist_ok=True)
        video_path = Path(prepared_media.video_path)

        def extract(index: int, timestamp: float) -> str:
            frame_path = layout.frames_dir / f"scene_{index:03d}.jpg"
            extract_frame(video_path, timestamp, frame_path)
            return str(frame_path)

        return build_slide_segments(
            scene_analysis,
            utterances,
            prepared_media.metadata.duration_sec,
            extract_frame=extract,
        )
