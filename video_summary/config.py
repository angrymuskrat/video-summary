from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

STEP_ORDER = (
    "prepare",
    "asr",
    "diarize",
    "align",
    "scenes",
    "slides",
    "summarize",
    "write",
    "render",
)
STEP_NUMBERS = {name: index for index, name in enumerate(STEP_ORDER, start=1)}


@dataclass(frozen=True)
class OutputLayout:
    output_dir: Path
    work_dir: Path
    frames_dir: Path
    state_path: Path
    work_video: Path
    audio_wav: Path
    transcript_txt: Path
    transcript_with_roles_txt: Path
    summary_md: Path
    transcript_json: Path
    subtitles_srt: Path
    subtitles_ass: Path
    video_subtitled_mp4: Path
    video_softsubs_mp4: Path
    slides_pptx: Path
    slides_pdf: Path


@dataclass(frozen=True)
class PipelineConfig:
    input_path: Path
    output_dir: Path
    hf_token: Optional[str] = None
    language: Optional[str] = None
    model: str = "large-v3"
    device: str = "cuda"
    compute_type: str = "float16"
    ffmpeg_video_encoder: str = "auto"
    presentation: str = "auto"
    scene_detector: str = "content"
    scene_threshold: Optional[float] = None
    min_scene_sec: float = 5.0
    num_speakers: Optional[int] = None
    min_speakers: Optional[int] = None
    max_speakers: Optional[int] = None
    subtitle_max_chars: int = 84
    subtitle_max_duration: float = 4.5
    transcript_gap: float = 0.8
    start_from: str = "prepare"
    export_pdf: bool = False
    keep_work_files: bool = False
    audio_path: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.start_from not in STEP_NUMBERS:
            raise ValueError(f"Unknown start_from step: {self.start_from}")

    @classmethod
    def from_paths(
        cls,
        input_path: str,
        output_dir: str,
        *,
        hf_token: Optional[str] = None,
        **kwargs: object,
    ) -> "PipelineConfig":
        return cls(
            input_path=Path(input_path).expanduser().resolve(),
            output_dir=Path(output_dir).expanduser().resolve(),
            hf_token=hf_token if hf_token is not None else os.environ.get("HF_TOKEN"),
            **kwargs,
        )

    def layout(self) -> OutputLayout:
        work_dir = self.output_dir / "_work"
        return OutputLayout(
            output_dir=self.output_dir,
            work_dir=work_dir,
            frames_dir=self.output_dir / "frames",
            state_path=self.output_dir / "pipeline_state.json",
            work_video=work_dir / "work.mp4",
            audio_wav=work_dir / "audio.wav",
            transcript_txt=self.output_dir / "transcript.txt",
            transcript_with_roles_txt=self.output_dir / "transcript_with_roles.txt",
            summary_md=self.output_dir / "summary.md",
            transcript_json=self.output_dir / "transcript.json",
            subtitles_srt=self.output_dir / "subtitles.srt",
            subtitles_ass=self.output_dir / "subtitles.ass",
            video_subtitled_mp4=self.output_dir / "video_subtitled.mp4",
            video_softsubs_mp4=self.output_dir / "video_softsubs.mp4",
            slides_pptx=self.output_dir / "slides.pptx",
            slides_pdf=self.output_dir / "slides.pdf",
        )

    def step_enabled(self, step_name: str) -> bool:
        return STEP_NUMBERS[self.start_from] <= STEP_NUMBERS[step_name]
