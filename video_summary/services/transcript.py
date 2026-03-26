from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any

from video_summary.domain.models import (
    AlignmentResult,
    MediaMetadata,
    PipelineArtifacts,
    SceneAnalysis,
    SceneSegment,
    SpeakerTurn,
    SummaryResult,
    Utterance,
    WordToken,
)


def format_ts(seconds: float, srt: bool = False) -> str:
    seconds = max(0.0, float(seconds))
    ms = int(round((seconds - math.floor(seconds)) * 1000))
    whole = int(math.floor(seconds))
    second = whole % 60
    minute = (whole // 60) % 60
    hour = whole // 3600
    if srt:
        return f"{hour:02d}:{minute:02d}:{second:02d},{ms:03d}"
    cs = ms // 10
    return f"{hour:d}:{minute:02d}:{second:02d}.{cs:02d}"


def clean_text_spacing(text: str) -> str:
    text = " ".join(text.strip().split())
    text = text.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
    text = text.replace(" :", ":").replace(" ;", ";")
    text = text.replace("( ", "(").replace(" )", ")")
    return text.strip()


def interval_overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def assign_speakers_to_words(words: list[WordToken], turns: list[SpeakerTurn]) -> list[WordToken]:
    copied = [WordToken(word.start, word.end, word.text, word.speaker) for word in words]
    if not turns:
        for word in copied:
            word.speaker = 1
        return copied

    turn_index = 0
    total_turns = len(turns)
    for word in copied:
        best_speaker = None
        best_overlap = -1.0
        midpoint = (word.start + word.end) / 2.0

        while turn_index + 1 < total_turns and turns[turn_index + 1].end <= word.start:
            turn_index += 1

        for candidate_index in range(max(0, turn_index - 2), min(total_turns, turn_index + 4)):
            turn = turns[candidate_index]
            overlap = interval_overlap(word.start, word.end, turn.start, turn.end)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = turn.speaker

        if best_overlap <= 0:
            nearest = min(turns, key=lambda turn: abs(((turn.start + turn.end) / 2.0) - midpoint))
            best_speaker = nearest.speaker

        word.speaker = best_speaker if best_speaker is not None else 1
    return copied


def build_utterances(words: list[WordToken], gap_sec: float = 0.8) -> list[Utterance]:
    if not words:
        return []

    ordered_words = sorted(words, key=lambda item: (item.start, item.end))
    output: list[Utterance] = []

    current_words = [ordered_words[0].text]
    current_start = ordered_words[0].start
    current_end = ordered_words[0].end
    current_speaker = ordered_words[0].speaker or 1

    for word in ordered_words[1:]:
        speaker = word.speaker or 1
        gap = word.start - current_end
        if speaker != current_speaker or gap > gap_sec:
            output.append(
                Utterance(
                    start=current_start,
                    end=current_end,
                    speaker=current_speaker,
                    text=clean_text_spacing(" ".join(current_words)),
                )
            )
            current_words = [word.text]
            current_start = word.start
            current_end = word.end
            current_speaker = speaker
        else:
            current_words.append(word.text)
            current_end = word.end

    output.append(
        Utterance(
            start=current_start,
            end=current_end,
            speaker=current_speaker,
            text=clean_text_spacing(" ".join(current_words)),
        )
    )
    return output


def build_subtitle_chunks(
    words: list[WordToken],
    max_chars: int = 84,
    max_duration: float = 4.5,
    gap_sec: float = 0.7,
) -> list[Utterance]:
    if not words:
        return []

    ordered_words = sorted(words, key=lambda item: (item.start, item.end))
    current: list[WordToken] = [ordered_words[0]]
    output: list[Utterance] = []

    for word in ordered_words[1:]:
        current_text = clean_text_spacing(" ".join(item.text for item in current))
        current_duration = current[-1].end - current[0].start
        same_speaker = (word.speaker or 1) == (current[-1].speaker or 1)
        gap = word.start - current[-1].end
        next_text = clean_text_spacing(current_text + " " + word.text)
        should_split = (
            not same_speaker
            or gap > gap_sec
            or current_duration >= max_duration
            or len(next_text) > max_chars
        )
        if should_split:
            speaker = current[0].speaker or 1
            text = clean_text_spacing(" ".join(item.text for item in current))
            output.append(Utterance(current[0].start, current[-1].end, speaker, f"[{speaker}] {text}"))
            current = [word]
        else:
            current.append(word)

    if current:
        speaker = current[0].speaker or 1
        text = clean_text_spacing(" ".join(item.text for item in current))
        output.append(Utterance(current[0].start, current[-1].end, speaker, f"[{speaker}] {text}"))

    return output


def render_transcript_text(
    utterances: list[Utterance],
    *,
    include_roles: bool,
    include_timestamps: bool = True,
) -> str:
    lines: list[str] = []
    for utterance in utterances:
        if include_timestamps:
            if include_roles:
                lines.append(
                    f"[{format_ts(utterance.start)} -> {format_ts(utterance.end)}] [S{utterance.speaker}]"
                )
            else:
                lines.append(f"[{format_ts(utterance.start)} -> {format_ts(utterance.end)}]")
        elif include_roles:
            lines.append(f"[S{utterance.speaker}]")
        lines.append(utterance.text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def transcript_payload(
    *,
    input_video: str,
    metadata: MediaMetadata,
    asr_meta: dict[str, Any],
    turns: list[SpeakerTurn],
    alignment: AlignmentResult,
    scene_analysis: SceneAnalysis,
    slide_segments: list[SceneSegment],
    summary: SummaryResult | None,
    artifacts: PipelineArtifacts,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "input_video": input_video,
        "duration_sec": metadata.duration_sec,
        "video": {
            "width": metadata.width,
            "height": metadata.height,
            "fps": metadata.fps,
        },
        "asr_meta": asr_meta,
        "speaker_turns": [asdict(turn) for turn in turns],
        "words": [asdict(word) for word in alignment.words],
        "utterances": [asdict(utterance) for utterance in alignment.utterances],
        "subtitles": [asdict(subtitle) for subtitle in alignment.subtitles],
        "scenes": [[scene.start, scene.end] for scene in scene_analysis.scenes],
        "has_presentation": scene_analysis.has_presentation,
        "slide_segments": [asdict(segment) for segment in slide_segments],
        "artifacts": {name: asdict(artifact) for name, artifact in artifacts.items.items()},
    }
    if summary is not None:
        payload["summary"] = asdict(summary)
    return payload
