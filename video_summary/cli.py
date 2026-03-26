from __future__ import annotations

import argparse
import os
from typing import Optional, Sequence

from video_summary.config import PipelineConfig, STEP_ORDER


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local pipeline for meeting video transcription + diarization + slides")
    parser.add_argument("--input", required=True, help="Input video file (.webm, .mp4, ...)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--hf-token", default=os.environ.get("HF_TOKEN"), help="Hugging Face token for pyannote")
    parser.add_argument("--language", default=None, help="Language code for ASR, e.g. ru, en")
    parser.add_argument("--model", default="large-v3", help="faster-whisper model: large-v3 | distil-large-v3 | turbo")
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"], help="Inference device")
    parser.add_argument("--compute-type", default="float16", help="faster-whisper compute type")
    parser.add_argument(
        "--ffmpeg-video-encoder",
        default="auto",
        choices=["auto", "h264_nvenc", "libx264"],
        help="Video encoder for ffmpeg. 'auto' prefers NVIDIA NVENC and falls back to libx264.",
    )
    parser.add_argument("--presentation", default="auto", choices=["auto", "yes", "no"], help="How to build slides")
    parser.add_argument("--scene-detector", default="content", choices=["content", "adaptive", "hash"])
    parser.add_argument("--scene-threshold", type=float, default=None)
    parser.add_argument("--min-scene-sec", type=float, default=5.0)
    parser.add_argument("--num-speakers", type=int, default=None)
    parser.add_argument("--min-speakers", type=int, default=None)
    parser.add_argument("--max-speakers", type=int, default=None)
    parser.add_argument("--subtitle-max-chars", type=int, default=84)
    parser.add_argument("--subtitle-max-duration", type=float, default=4.5)
    parser.add_argument("--transcript-gap", type=float, default=0.8)
    parser.add_argument(
        "--start-from",
        default="prepare",
        choices=list(STEP_ORDER),
        help="Start pipeline from a specific step. Useful for debugging with existing intermediate artifacts.",
    )
    parser.add_argument("--export-pdf", action="store_true")
    parser.add_argument("--keep-work-files", action="store_true")
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def config_from_args(args: argparse.Namespace) -> PipelineConfig:
    return PipelineConfig.from_paths(
        args.input,
        args.output_dir,
        hf_token=args.hf_token,
        language=args.language,
        model=args.model,
        device=args.device,
        compute_type=args.compute_type,
        ffmpeg_video_encoder=args.ffmpeg_video_encoder,
        presentation=args.presentation,
        scene_detector=args.scene_detector,
        scene_threshold=args.scene_threshold,
        min_scene_sec=args.min_scene_sec,
        num_speakers=args.num_speakers,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
        subtitle_max_chars=args.subtitle_max_chars,
        subtitle_max_duration=args.subtitle_max_duration,
        transcript_gap=args.transcript_gap,
        start_from=args.start_from,
        export_pdf=args.export_pdf,
        keep_work_files=args.keep_work_files,
    )
