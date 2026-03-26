from __future__ import annotations

from pathlib import Path

from video_summary.config import PipelineConfig
from video_summary.domain.models import MediaMetadata, SceneAnalysis, SceneBoundary
from video_summary.services import decide_has_presentation, merge_short_scenes


class PySceneDetectSceneDetector:
    def detect(self, video_path: str, metadata: MediaMetadata, config: PipelineConfig) -> SceneAnalysis:
        from scenedetect import detect
        from scenedetect.detectors import AdaptiveDetector, ContentDetector, HashDetector

        min_scene_len = max(15, int(round(metadata.fps * config.min_scene_sec)))
        if config.scene_detector == "content":
            detector = ContentDetector(
                threshold=config.scene_threshold if config.scene_threshold is not None else 27.0,
                min_scene_len=min_scene_len,
            )
        elif config.scene_detector == "adaptive":
            detector = AdaptiveDetector(
                adaptive_threshold=config.scene_threshold if config.scene_threshold is not None else 3.0,
                min_scene_len=min_scene_len,
            )
        elif config.scene_detector == "hash":
            detector = HashDetector(
                threshold=config.scene_threshold if config.scene_threshold is not None else 0.18,
                min_scene_len=min_scene_len,
            )
        else:
            raise ValueError(f"Unknown scene detector: {config.scene_detector}")

        raw_scenes = detect(str(Path(video_path)), detector, show_progress=True)
        scenes = [SceneBoundary(start=float(start.get_seconds()), end=float(end.get_seconds())) for start, end in raw_scenes]
        merged_scenes = merge_short_scenes(scenes, min_keep_sec=max(config.min_scene_sec, 6.0))

        if config.presentation == "yes":
            has_presentation = True
        elif config.presentation == "no":
            has_presentation = False
        else:
            has_presentation = decide_has_presentation(merged_scenes, metadata.duration_sec)
        return SceneAnalysis(scenes=merged_scenes, has_presentation=has_presentation)
