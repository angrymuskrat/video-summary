from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

import numpy as np

from video_summary.adapters.media.ffmpeg import is_cuda_runtime_error
from video_summary.config import PipelineConfig
from video_summary.domain.models import SpeakerTurn


class PyannoteDiarization:
    def diarize(self, audio_path: str, config: PipelineConfig) -> list[SpeakerTurn]:
        import torch
        from pyannote.audio import Pipeline

        if not config.hf_token:
            raise RuntimeError("Hugging Face token is required for pyannote diarization.")

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-community-1",
            token=config.hf_token,
        )
        if config.device == "cuda":
            try:
                pipeline.to(torch.device("cuda"))
            except RuntimeError as exc:
                if not is_cuda_runtime_error(exc):
                    raise

        kwargs: dict[str, Any] = {}
        if config.num_speakers is not None:
            kwargs["num_speakers"] = config.num_speakers
        if config.min_speakers is not None:
            kwargs["min_speakers"] = config.min_speakers
        if config.max_speakers is not None:
            kwargs["max_speakers"] = config.max_speakers

        audio_input: Any = str(Path(audio_path))
        try:
            with wave.open(str(audio_path), "rb") as wav_file:
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                sample_rate = wav_file.getframerate()
                frame_count = wav_file.getnframes()
                raw_bytes = wav_file.readframes(frame_count)
            if sample_width == 2:
                pcm = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                if channels > 1:
                    pcm = pcm.reshape(-1, channels).T
                else:
                    pcm = pcm.reshape(1, -1)
                waveform = torch.from_numpy(np.ascontiguousarray(pcm))
                audio_input = {"waveform": waveform, "sample_rate": sample_rate, "uri": Path(audio_path).stem}
        except (wave.Error, OSError, ValueError):
            audio_input = str(Path(audio_path))

        diarization = pipeline(audio_input, **kwargs)
        annotation = getattr(diarization, "speaker_diarization", diarization)
        raw_turns: list[tuple[float, float, str]] = []
        if hasattr(annotation, "itertracks"):
            for turn, _track, label in annotation.itertracks(yield_label=True):
                raw_turns.append((float(turn.start), float(turn.end), str(label)))
        else:
            for item in annotation:
                if len(item) == 2:
                    turn, label = item
                    raw_turns.append((float(turn.start), float(turn.end), str(label)))
                elif len(item) == 3:
                    turn, _track, label = item
                    raw_turns.append((float(turn.start), float(turn.end), str(label)))

        raw_turns.sort(key=lambda item: (item[0], item[1]))
        label_map: dict[str, int] = {}
        next_id = 1
        turns: list[SpeakerTurn] = []
        for start, end, label in raw_turns:
            if label not in label_map:
                label_map[label] = next_id
                next_id += 1
            turns.append(SpeakerTurn(start=start, end=end, speaker=label_map[label]))
        return turns
