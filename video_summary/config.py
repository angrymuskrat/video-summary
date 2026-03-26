"""Configuration models and output path layout helpers for pipeline runs."""


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
    """Output layout.
    
    Attributes:
        output_dir (Path): Stored value for output dir.
        work_dir (Path): Stored value for work dir.
        frames_dir (Path): Stored value for frames dir.
        state_path (Path): Stored value for state path.
        work_video (Path): Stored value for work video.
        audio_wav (Path): Stored value for audio wav.
        transcript_txt (Path): Stored value for transcript txt.
        transcript_with_roles_txt (Path): Stored value for transcript with roles txt.
        summary_md (Path): Stored value for summary md.
        transcript_json (Path): Stored value for transcript json.
        subtitles_srt (Path): Stored value for subtitles srt.
        subtitles_ass (Path): Stored value for subtitles ass.
        video_subtitled_mp4 (Path): Stored value for video subtitled mp4.
        video_softsubs_mp4 (Path): Stored value for video softsubs mp4.
        slides_pptx (Path): Stored value for slides pptx.
        slides_pdf (Path): Stored value for slides pdf.
    """
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
    """Pipeline config.
    
    Attributes:
        input_path (Path): Stored value for input path.
        output_dir (Path): Stored value for output dir.
        hf_token (Optional[str]): Stored value for hf token.
        language (Optional[str]): Stored value for language.
        model (str): Stored value for model.
        device (str): Stored value for device.
        compute_type (str): Stored value for compute type.
        ffmpeg_video_encoder (str): Stored value for ffmpeg video encoder.
        presentation (str): Stored value for presentation.
        scene_detector (str): Stored value for scene detector.
        scene_threshold (Optional[float]): Stored value for scene threshold.
        min_scene_sec (float): Stored value for min scene sec.
        num_speakers (Optional[int]): Stored value for num speakers.
        min_speakers (Optional[int]): Stored value for min speakers.
        max_speakers (Optional[int]): Stored value for max speakers.
        subtitle_max_chars (int): Stored value for subtitle max chars.
        subtitle_max_duration (float): Stored value for subtitle max duration.
        transcript_gap (float): Stored value for transcript gap.
        start_from (str): Stored value for start from.
        export_pdf (bool): Stored value for export pdf.
        keep_work_files (bool): Stored value for keep work files.
        audio_path (Optional[Path]): Stored value for audio path.
        summarizer_provider (str): Stored value for summarizer provider.
        openai_api_key (Optional[str]): Stored value for openai api key.
        openai_model (Optional[str]): Stored value for openai model.
        openai_base_url (Optional[str]): Stored value for openai base url.
        openai_timeout_sec (float): Stored value for openai timeout sec.
    """
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
    summarizer_provider: str = "basic"
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_timeout_sec: float = 60.0

    def __post_init__(self) -> None:
        """Validate and normalize dataclass state after initialization."""
        if self.start_from not in STEP_NUMBERS:
            raise ValueError(f"Unknown start_from step: {self.start_from}")
        if self.summarizer_provider not in {"basic", "openai"}:
            raise ValueError(f"Unknown summarizer_provider: {self.summarizer_provider}")

    @classmethod
    def from_paths(
        cls,
        input_path: str,
        output_dir: str,
        *,
        hf_token: Optional[str] = None,
        **kwargs: object,
    ) -> "PipelineConfig":
        """Create a pipeline config from paths.
        
        Args:
            input_path (str): Filesystem path for input.
            output_dir (str): Value for output dir.
            hf_token (Optional[str]): Optional keyword-only value for hf token.
            **kwargs (object): Additional keyword arguments.
        
        Returns:
            'PipelineConfig': Result produced by from paths.
        """
        return cls(
            input_path=Path(input_path).expanduser().resolve(),
            output_dir=Path(output_dir).expanduser().resolve(),
            hf_token=hf_token if hf_token is not None else os.environ.get("HF_TOKEN"),
            openai_api_key=str(kwargs.pop("openai_api_key", os.environ.get("OPENAI_API_KEY") or "")) or None,
            openai_model=str(kwargs.pop("openai_model", os.environ.get("OPENAI_MODEL") or "")) or None,
            openai_base_url=str(kwargs.pop("openai_base_url", os.environ.get("OPENAI_BASE_URL") or "")) or None,
            summarizer_provider=str(
                kwargs.pop("summarizer_provider", os.environ.get("VIDEO_SUMMARY_SUMMARIZER_PROVIDER") or "basic")
            ),
            openai_timeout_sec=float(kwargs.pop("openai_timeout_sec", os.environ.get("OPENAI_TIMEOUT_SEC", 60.0))),
            **kwargs,
        )

    def layout(self) -> OutputLayout:
        """Build the output layout for the configured run.
        
        Returns:
            OutputLayout: Result produced by layout.
        """
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
        """Return whether the named step should run.
        
        Args:
            step_name (str): Value for step name.
        
        Returns:
            bool: Result produced by step enabled.
        """
        return STEP_NUMBERS[self.start_from] <= STEP_NUMBERS[step_name]
