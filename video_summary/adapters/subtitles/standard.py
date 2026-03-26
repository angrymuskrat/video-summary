from __future__ import annotations

from pathlib import Path

from video_summary.config import PipelineConfig
from video_summary.domain.models import ArtifactRecord, MediaMetadata, Utterance
from video_summary.services import format_ts


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


class StandardSubtitleGenerator:
    def generate(
        self,
        subtitles: list[Utterance],
        metadata: MediaMetadata,
        config: PipelineConfig,
    ) -> list[ArtifactRecord]:
        layout = config.layout()
        layout.output_dir.mkdir(parents=True, exist_ok=True)
        self._write_srt(subtitles, layout.subtitles_srt)
        self._write_ass(subtitles, layout.subtitles_ass, metadata.width, metadata.height)
        return [
            ArtifactRecord(name="subtitles_srt", path=str(layout.subtitles_srt), kind="text"),
            ArtifactRecord(name="subtitles_ass", path=str(layout.subtitles_ass), kind="text"),
        ]

    def _write_srt(self, subtitles: list[Utterance], out_path: Path) -> None:
        lines: list[str] = []
        for index, subtitle in enumerate(subtitles, start=1):
            lines.append(str(index))
            lines.append(f"{format_ts(subtitle.start, srt=True)} --> {format_ts(subtitle.end, srt=True)}")
            lines.append(subtitle.text)
            lines.append("")
        out_path.write_text("\n".join(lines), encoding="utf-8")

    def _write_ass(self, subtitles: list[Utterance], out_path: Path, width: int, height: int) -> None:
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes
WrapStyle: 0
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,Arial,28,&H00FFFFFF,&H0000FFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,40,40,26,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
        lines = [header.rstrip()]
        for subtitle in subtitles:
            lines.append(
                f"Dialogue: 0,{format_ts(subtitle.start)},{format_ts(subtitle.end)},Default,,0,0,0,,{ass_escape(subtitle.text)}"
            )
        out_path.write_text("\n".join(lines), encoding="utf-8")
