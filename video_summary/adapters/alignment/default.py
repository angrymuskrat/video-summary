"""Concrete implementation of alignment for the video summary pipeline."""


from __future__ import annotations

from video_summary.config import PipelineConfig
from video_summary.domain.models import AlignmentResult, SpeakerTurn, WordToken
from video_summary.services import assign_speakers_to_words, build_subtitle_chunks, build_utterances


class DefaultAlignmentEngine:
    """Engine for default alignment."""
    def align(
        self,
        words: list[WordToken],
        turns: list[SpeakerTurn],
        config: PipelineConfig,
    ) -> AlignmentResult:
        """Align the requested pipeline data.
        
        Args:
            words (list[WordToken]): Value for words.
            turns (list[SpeakerTurn]): Value for turns.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            AlignmentResult: Result produced by align.
        """
        aligned_words = assign_speakers_to_words(words, turns)
        utterances = build_utterances(aligned_words, gap_sec=config.transcript_gap)
        subtitles = build_subtitle_chunks(
            aligned_words,
            max_chars=config.subtitle_max_chars,
            max_duration=config.subtitle_max_duration,
            gap_sec=min(0.7, config.transcript_gap),
        )
        return AlignmentResult(words=aligned_words, utterances=utterances, subtitles=subtitles)
