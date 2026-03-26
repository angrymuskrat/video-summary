from __future__ import annotations

from typing import Callable

from video_summary.domain.models import SceneAnalysis, SceneBoundary, SceneSegment, Utterance
from video_summary.services.transcript import interval_overlap


def merge_short_scenes(scenes: list[SceneBoundary], min_keep_sec: float) -> list[SceneBoundary]:
    if not scenes:
        return []

    merged: list[SceneBoundary] = []
    current = SceneBoundary(scenes[0].start, scenes[0].end)
    for scene in scenes[1:]:
        if (current.end - current.start) < min_keep_sec:
            current.end = scene.end
        else:
            merged.append(current)
            current = SceneBoundary(scene.start, scene.end)
    merged.append(current)
    return merged


def decide_has_presentation(scenes: list[SceneBoundary], total_duration: float) -> bool:
    if len(scenes) < 2:
        return False
    long_scenes = [scene for scene in scenes if (scene.end - scene.start) >= 8.0]
    long_coverage = sum(scene.end - scene.start for scene in long_scenes) / max(1e-6, total_duration)
    return len(long_scenes) >= 2 and long_coverage >= 0.35


def utterances_overlapping(
    utterances: list[Utterance],
    start: float,
    end: float,
    pad: float = 1.0,
) -> list[Utterance]:
    query_start = max(0.0, start - pad)
    query_end = end + pad
    return [
        utterance
        for utterance in utterances
        if interval_overlap(utterance.start, utterance.end, query_start, query_end) > 0
    ]


def trim_slide_text(text: str, max_chars: int = 1700) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def build_slide_segments(
    scene_analysis: SceneAnalysis,
    utterances: list[Utterance],
    duration_sec: float,
    *,
    extract_frame: Callable[[int, float], str],
) -> list[SceneSegment]:
    if not scene_analysis.has_presentation or not scene_analysis.scenes:
        frame_path = extract_frame(1, duration_sec / 2.0)
        text = "\n".join(f"[{utterance.speaker}] {utterance.text}" for utterance in utterances)
        return [
            SceneSegment(
                index=1,
                start=0.0,
                end=duration_sec,
                frame_path=frame_path,
                text=trim_slide_text(text),
                utterance_count=len(utterances),
            )
        ]

    slides: list[SceneSegment] = []
    for index, scene in enumerate(scene_analysis.scenes, start=1):
        timestamp = max(scene.start, min((scene.start + scene.end) / 2.0, max(scene.start + 0.1, scene.end - 0.1)))
        frame_path = extract_frame(index, timestamp)
        overlapping = utterances_overlapping(utterances, scene.start, scene.end, pad=1.0)
        text = "\n".join(f"[{utterance.speaker}] {utterance.text}" for utterance in overlapping)
        slides.append(
            SceneSegment(
                index=index,
                start=scene.start,
                end=scene.end,
                frame_path=frame_path,
                text=trim_slide_text(text),
                utterance_count=len(overlapping),
            )
        )
    return slides
