"""Tests for transcript services behavior in the video summary package."""


from video_summary.domain.models import SpeakerTurn, Utterance, WordToken
from video_summary.services import assign_speakers_to_words, build_subtitle_chunks, build_utterances


def test_assign_speakers_to_words_uses_overlap_then_nearest_turn() -> None:
    """Test that assign speakers to words uses overlap then nearest turn."""
    words = [
        WordToken(0.0, 0.5, "hello"),
        WordToken(1.5, 2.0, "world"),
        WordToken(3.5, 4.0, "again"),
    ]
    turns = [
        SpeakerTurn(0.0, 1.0, 1),
        SpeakerTurn(1.0, 3.0, 2),
        SpeakerTurn(4.5, 5.0, 3),
    ]

    assigned = assign_speakers_to_words(words, turns)

    assert [word.speaker for word in assigned] == [1, 2, 3]


def test_build_utterances_splits_on_speaker_and_gap() -> None:
    """Test that build utterances splits on speaker and gap."""
    words = [
        WordToken(0.0, 0.4, "hello", 1),
        WordToken(0.5, 0.8, "there", 1),
        WordToken(2.0, 2.4, "new", 1),
        WordToken(2.5, 2.8, "speaker", 2),
    ]

    utterances = build_utterances(words, gap_sec=0.7)

    assert utterances == [
        Utterance(0.0, 0.8, 1, "hello there"),
        Utterance(2.0, 2.4, 1, "new"),
        Utterance(2.5, 2.8, 2, "speaker"),
    ]


def test_build_subtitle_chunks_respects_length_and_speaker_boundaries() -> None:
    """Test that build subtitle chunks respects length and speaker boundaries."""
    words = [
        WordToken(0.0, 0.4, "hello", 1),
        WordToken(0.5, 0.8, "team", 1),
        WordToken(1.0, 1.3, "switch", 2),
    ]

    subtitles = build_subtitle_chunks(words, max_chars=20, max_duration=4.5, gap_sec=0.7)

    assert subtitles == [
        Utterance(0.0, 0.8, 1, "[1] hello team"),
        Utterance(1.0, 1.3, 2, "[2] switch"),
    ]
