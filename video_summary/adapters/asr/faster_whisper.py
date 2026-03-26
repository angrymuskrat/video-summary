"""Concrete implementation of speech-to-text for the video summary pipeline."""


from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from video_summary.adapters.media.ffmpeg import is_cuda_runtime_error, normalize_compute_type
from video_summary.config import PipelineConfig
from video_summary.domain.models import WordToken
from video_summary.services import clean_text_spacing


class FasterWhisperASR:
    """Faster whisper a s r."""
    def transcribe(self, audio_path: str, config: PipelineConfig) -> tuple[list[WordToken], dict[str, Any]]:
        """Transcribe the requested pipeline data.
        
        Args:
            audio_path (str): Filesystem path for audio.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            tuple[list[WordToken], dict[str, Any]]: Result produced by transcribe.
        """
        from faster_whisper import WhisperModel

        model_name = config.model
        language = config.language
        resolved_device = config.device
        resolved_compute_type = normalize_compute_type(config.device, config.compute_type)

        def run_transcribe(device_name: str, compute_name: str) -> tuple[list[Any], Any]:
            """Run transcribe.
            
            Args:
                device_name (str): Value for device name.
                compute_name (str): Value for compute name.
            
            Returns:
                tuple[list[Any], Any]: Result produced by run transcribe.
            """
            model = WhisperModel(model_name, device=device_name, compute_type=compute_name)
            segments_gen, info_obj = model.transcribe(
                str(Path(audio_path)),
                beam_size=5,
                language=language,
                word_timestamps=True,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                condition_on_previous_text=False,
            )
            return list(segments_gen), info_obj

        try:
            segments, info = run_transcribe(resolved_device, resolved_compute_type)
        except RuntimeError as exc:
            if resolved_device == "cuda" and is_cuda_runtime_error(exc):
                resolved_device = "cpu"
                resolved_compute_type = "int8"
                segments, info = run_transcribe(resolved_device, resolved_compute_type)
            else:
                raise

        words: list[WordToken] = []
        for segment in segments:
            segment_words = getattr(segment, "words", None)
            if segment_words:
                for word in segment_words:
                    if word.start is None or word.end is None:
                        continue
                    token_text = clean_text_spacing(getattr(word, "word", ""))
                    if token_text:
                        words.append(WordToken(float(word.start), float(word.end), token_text))
            else:
                text = clean_text_spacing(getattr(segment, "text", ""))
                if text:
                    words.append(WordToken(float(segment.start), float(segment.end), text))

        meta = {
            "language": getattr(info, "language", language),
            "language_probability": getattr(info, "language_probability", None),
            "model_name": model_name,
            "device": resolved_device,
            "compute_type": resolved_compute_type,
            "segment_count": len(segments),
            "word_count": len(words),
        }
        return words, meta
