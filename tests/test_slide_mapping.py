"""Tests for slide mapping behavior in the video summary package."""


from video_summary.domain.models import SceneAnalysis, SceneBoundary, Utterance
from video_summary.services import build_slide_segments, merge_short_scenes


def test_merge_short_scenes_collapses_short_segments_into_next_scene() -> None:
    """Test that merge short scenes collapses short segments into next scene."""
    scenes = [SceneBoundary(0.0, 2.0), SceneBoundary(2.0, 10.0), SceneBoundary(10.0, 12.0)]

    merged = merge_short_scenes(scenes, min_keep_sec=5.0)

    assert merged == [SceneBoundary(0.0, 10.0), SceneBoundary(10.0, 12.0)]


def test_build_slide_segments_creates_single_slide_without_presentation() -> None:
    """Test that build slide segments creates single slide without presentation."""
    extracted: list[tuple[int, float]] = []

    def fake_extract(index: int, timestamp: float) -> str:
        """Fake extract.
        
        Args:
            index (int): Value for index.
            timestamp (float): Value for timestamp.
        
        Returns:
            str: Result produced by fake extract.
        """
        extracted.append((index, timestamp))
        return f"frame-{index}.jpg"

    slides = build_slide_segments(
        SceneAnalysis(scenes=[], has_presentation=False),
        [Utterance(0.0, 1.0, 1, "hello")],
        20.0,
        extract_frame=fake_extract,
    )

    assert slides[0].frame_path == "frame-1.jpg"
    assert slides[0].text == "[1] hello"
    assert extracted == [(1, 10.0)]


def test_build_slide_segments_binds_overlapping_utterances_to_each_scene() -> None:
    """Test that build slide segments binds overlapping utterances to each scene."""
    def fake_extract(index: int, timestamp: float) -> str:
        """Fake extract.
        
        Args:
            index (int): Value for index.
            timestamp (float): Value for timestamp.
        
        Returns:
            str: Result produced by fake extract.
        """
        return f"scene-{index}@{timestamp:.1f}.jpg"

    slides = build_slide_segments(
        SceneAnalysis(
            scenes=[SceneBoundary(0.0, 5.0), SceneBoundary(5.0, 10.0)],
            has_presentation=True,
        ),
        [
            Utterance(0.1, 1.0, 1, "intro"),
            Utterance(6.0, 7.0, 2, "details"),
        ],
        10.0,
        extract_frame=fake_extract,
    )

    assert slides[0].text == "[1] intro"
    assert slides[1].text == "[2] details"
