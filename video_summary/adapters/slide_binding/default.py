"""Concrete implementation of slide binding for the video summary pipeline."""


from __future__ import annotations

from pathlib import Path

from video_summary.adapters.media.ffmpeg import extract_frame
from video_summary.config import PipelineConfig
from video_summary.domain.models import PreparedMedia, SceneAnalysis, SceneSegment, Utterance
from video_summary.services import build_slide_segments


class DefaultSlideBinder:
    """Default slide binder."""
    def bind(
        self,
        scene_analysis: SceneAnalysis,
        utterances: list[Utterance],
        prepared_media: PreparedMedia,
        config: PipelineConfig,
    ) -> list[SceneSegment]:
        """Bind the requested pipeline data.
        
        Args:
            scene_analysis (SceneAnalysis): Value for scene analysis.
            utterances (list[Utterance]): Value for utterances.
            prepared_media (PreparedMedia): Value for prepared media.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            list[SceneSegment]: Result produced by bind.
        """
        layout = config.layout()
        layout.frames_dir.mkdir(parents=True, exist_ok=True)
        video_path = Path(prepared_media.video_path)

        def extract(index: int, timestamp: float) -> str:
            """Extract.
            
            Args:
                index (int): Value for index.
                timestamp (float): Value for timestamp.
            
            Returns:
                str: Result produced by extract.
            """
            frame_path = layout.frames_dir / f"scene_{index:03d}.jpg"
            extract_frame(video_path, timestamp, frame_path)
            return str(frame_path)

        return build_slide_segments(
            scene_analysis,
            utterances,
            prepared_media.metadata.duration_sec,
            extract_frame=extract,
        )
