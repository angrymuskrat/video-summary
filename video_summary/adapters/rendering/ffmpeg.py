from __future__ import annotations

import subprocess
from pathlib import Path

from video_summary.adapters.media.ffmpeg import resolve_ffmpeg_video_encoder, run_command, video_encode_args
from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, PreparedMedia


class FFmpegVideoRenderer:
    def render(self, prepared_media: PreparedMedia, config: PipelineConfig) -> list[ArtifactRecord]:
        layout = config.layout()
        layout.output_dir.mkdir(parents=True, exist_ok=True)
        video_encoder = resolve_ffmpeg_video_encoder(config.ffmpeg_video_encoder)
        hard_ok = False
        try:
            self._burn_subtitles_hard(Path(prepared_media.video_path), layout.subtitles_ass, layout.video_subtitled_mp4, video_encoder)
            hard_ok = True
        except subprocess.CalledProcessError:
            hard_ok = False
        self._mux_subtitles_soft(Path(prepared_media.video_path), layout.subtitles_srt, layout.video_softsubs_mp4)

        artifacts = [ArtifactRecord(name="video_softsubs", path=str(layout.video_softsubs_mp4), kind="video")]
        if hard_ok:
            artifacts.insert(0, ArtifactRecord(name="video_subtitled", path=str(layout.video_subtitled_mp4), kind="video"))
        return artifacts

    def _burn_subtitles_hard(self, work_video: Path, ass_file: Path, output_video: Path, video_encoder: str) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(work_video),
            "-vf",
            f"subtitles={ass_file.name}",
            *video_encode_args(video_encoder),
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_video),
        ]
        try:
            run_command(cmd, cwd=ass_file.parent)
        except subprocess.CalledProcessError:
            if video_encoder == "libx264":
                raise
            fallback_cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(work_video),
                "-vf",
                f"subtitles={ass_file.name}",
                *video_encode_args("libx264"),
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                str(output_video),
            ]
            run_command(fallback_cmd, cwd=ass_file.parent)

    def _mux_subtitles_soft(self, work_video: Path, srt_file: Path, output_video: Path) -> None:
        run_command(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(work_video),
                "-i",
                str(srt_file),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                "-map",
                "1:0",
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                "-c:s",
                "mov_text",
                str(output_video),
            ]
        )
