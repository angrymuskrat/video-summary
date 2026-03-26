"""Concrete implementation of media preparation for the video summary pipeline."""


from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional, Sequence

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource, MediaMetadata, PreparedMedia


def run_command(
    cmd: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run command.
    
    Args:
        cmd (Sequence[str]): Value for cmd.
        cwd (Optional[Path]): Optional keyword-only value for cwd.
        capture (bool): Optional keyword-only value for capture.
    
    Returns:
        subprocess.CompletedProcess[str]: Result produced by run command.
    """
    kwargs: dict[str, Any] = {
        "cwd": str(cwd) if cwd else None,
        "check": True,
        "text": True,
    }
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    return subprocess.run(list(cmd), **kwargs)


def ensure_tool(name: str) -> None:
    """Ensure tool.
    
    Args:
        name (str): Value for name.
    """
    if shutil.which(name) is None:
        raise RuntimeError(f"Required tool '{name}' was not found in PATH.")


def ffmpeg_supports_encoder(encoder: str) -> bool:
    """Ffmpeg supports encoder.
    
    Args:
        encoder (str): Value for encoder.
    
    Returns:
        bool: Result produced by ffmpeg supports encoder.
    """
    try:
        out = run_command(["ffmpeg", "-hide_banner", "-encoders"], capture=True)
    except subprocess.CalledProcessError:
        return False
    return encoder in out.stdout


def resolve_ffmpeg_video_encoder(requested: str) -> str:
    """Resolve ffmpeg video encoder.
    
    Args:
        requested (str): Value for requested.
    
    Returns:
        str: Result produced by resolve ffmpeg video encoder.
    """
    if requested == "auto":
        return "h264_nvenc" if ffmpeg_supports_encoder("h264_nvenc") else "libx264"
    return requested


def video_encode_args(encoder: str) -> list[str]:
    """Video encode args.
    
    Args:
        encoder (str): Value for encoder.
    
    Returns:
        list[str]: Result produced by video encode args.
    """
    if encoder == "h264_nvenc":
        return [
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p5",
            "-cq",
            "23",
            "-b:v",
            "0",
            "-pix_fmt",
            "yuv420p",
        ]
    return [
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
    ]


def ffprobe_json(input_path: Path) -> dict[str, Any]:
    """Ffprobe json.
    
    Args:
        input_path (Path): Filesystem path for input.
    
    Returns:
        dict[str, Any]: Result produced by ffprobe json.
    """
    out = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(input_path),
        ],
        capture=True,
    )
    return json.loads(out.stdout)


def parse_fps(r_frame_rate: str) -> float:
    """Parse fps.
    
    Args:
        r_frame_rate (str): Value for r frame rate.
    
    Returns:
        float: Result produced by parse fps.
    """
    if not r_frame_rate or r_frame_rate == "0/0":
        return 25.0
    numerator, denominator = r_frame_rate.split("/")
    numerator_f = float(numerator)
    denominator_f = float(denominator)
    return numerator_f / denominator_f if denominator_f else 25.0


def ensure_work_mp4(input_video: Path, work_video: Path, video_encoder: str) -> None:
    """Ensure work mp4.
    
    Args:
        input_video (Path): Value for input video.
        work_video (Path): Value for work video.
        video_encoder (str): Value for video encoder.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        *video_encode_args(video_encoder),
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(work_video),
    ]
    try:
        run_command(cmd)
    except subprocess.CalledProcessError:
        if video_encoder == "libx264":
            raise
        fallback_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_video),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            *video_encode_args("libx264"),
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(work_video),
        ]
        run_command(fallback_cmd)


def extract_audio(input_media: Path, audio_wav: Path) -> None:
    """Extract audio.
    
    Args:
        input_media (Path): Value for input media.
        audio_wav (Path): Value for audio wav.
    """
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_media),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio_wav),
        ]
    )


def extract_frame(video_path: Path, ts_sec: float, out_path: Path) -> None:
    """Extract frame.
    
    Args:
        video_path (Path): Filesystem path for video.
        ts_sec (float): Value for ts sec.
        out_path (Path): Filesystem path for out.
    """
    run_command(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{ts_sec:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out_path),
        ]
    )


def is_cuda_runtime_error(exc: BaseException) -> bool:
    """Is cuda runtime error.
    
    Args:
        exc (BaseException): Value for exc.
    
    Returns:
        bool: Result produced by is cuda runtime error.
    """
    message = str(exc).lower()
    markers = ("cublas", "cudnn", "cuda", "cannot be loaded", "not found", "failed to load")
    return any(marker in message for marker in markers)


def normalize_compute_type(device: str, compute_type: str) -> str:
    """Normalize compute type.
    
    Args:
        device (str): Value for device.
        compute_type (str): Value for compute type.
    
    Returns:
        str: Result produced by normalize compute type.
    """
    if device == "cpu" and compute_type in {"float16", "int8_float16", "bfloat16"}:
        return "int8"
    return compute_type


class FFmpegMediaPreparator:
    """F fmpeg media preparator."""
    def prepare(self, source: InputSource, config: PipelineConfig) -> PreparedMedia:
        """Prepare the requested pipeline data.
        
        Args:
            source (InputSource): Value for source.
            config (PipelineConfig): Pipeline configuration to use for the operation.
        
        Returns:
            PreparedMedia: Result produced by prepare.
        """
        layout = config.layout()
        layout.output_dir.mkdir(parents=True, exist_ok=True)
        layout.work_dir.mkdir(parents=True, exist_ok=True)

        ensure_tool("ffmpeg")
        ensure_tool("ffprobe")

        input_video = Path(source.video_path)
        encoder = resolve_ffmpeg_video_encoder(config.ffmpeg_video_encoder)
        ensure_work_mp4(input_video, layout.work_video, encoder)
        extract_audio(Path(source.audio_path) if source.audio_path else layout.work_video, layout.audio_wav)

        probe = ffprobe_json(layout.work_video)
        video_stream = next((stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"), None)
        metadata = MediaMetadata(
            duration_sec=float(probe["format"]["duration"]),
            width=int(video_stream.get("width", 1920)) if video_stream else 1920,
            height=int(video_stream.get("height", 1080)) if video_stream else 1080,
            fps=parse_fps(video_stream.get("r_frame_rate", "25/1")) if video_stream else 25.0,
        )
        return PreparedMedia(video_path=str(layout.work_video), audio_path=str(layout.audio_wav), metadata=metadata)
