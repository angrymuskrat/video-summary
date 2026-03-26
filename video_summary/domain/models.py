from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class WordToken:
    start: float
    end: float
    text: str
    speaker: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WordToken":
        return cls(
            start=float(data["start"]),
            end=float(data["end"]),
            text=str(data["text"]),
            speaker=int(data["speaker"]) if data.get("speaker") is not None else None,
        )


@dataclass(slots=True)
class SpeakerTurn:
    start: float
    end: float
    speaker: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpeakerTurn":
        return cls(
            start=float(data["start"]),
            end=float(data["end"]),
            speaker=int(data["speaker"]),
        )


@dataclass(slots=True)
class Utterance:
    start: float
    end: float
    speaker: int
    text: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Utterance":
        return cls(
            start=float(data["start"]),
            end=float(data["end"]),
            speaker=int(data["speaker"]),
            text=str(data["text"]),
        )


@dataclass(slots=True)
class SceneBoundary:
    start: float
    end: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneBoundary":
        return cls(start=float(data["start"]), end=float(data["end"]))


@dataclass(slots=True)
class SceneSegment:
    index: int
    start: float
    end: float
    frame_path: str
    text: str
    utterance_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneSegment":
        return cls(
            index=int(data["index"]),
            start=float(data["start"]),
            end=float(data["end"]),
            frame_path=str(data["frame_path"]),
            text=str(data["text"]),
            utterance_count=int(data["utterance_count"]),
        )


@dataclass(slots=True)
class MediaMetadata:
    duration_sec: float
    width: int
    height: int
    fps: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MediaMetadata":
        return cls(
            duration_sec=float(data["duration_sec"]),
            width=int(data["width"]),
            height=int(data["height"]),
            fps=float(data["fps"]),
        )


@dataclass(slots=True)
class InputSource:
    video_path: str
    audio_path: Optional[str] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InputSource":
        return cls(
            video_path=str(data["video_path"]),
            audio_path=str(data["audio_path"]) if data.get("audio_path") else None,
            title=str(data["title"]) if data.get("title") else None,
        )


@dataclass(slots=True)
class PreparedMedia:
    video_path: str
    audio_path: str
    metadata: MediaMetadata

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreparedMedia":
        return cls(
            video_path=str(data["video_path"]),
            audio_path=str(data["audio_path"]),
            metadata=MediaMetadata.from_dict(data["metadata"]),
        )


@dataclass(slots=True)
class AlignmentResult:
    words: list[WordToken] = field(default_factory=list)
    utterances: list[Utterance] = field(default_factory=list)
    subtitles: list[Utterance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AlignmentResult":
        return cls(
            words=[WordToken.from_dict(item) for item in data.get("words", [])],
            utterances=[Utterance.from_dict(item) for item in data.get("utterances", [])],
            subtitles=[Utterance.from_dict(item) for item in data.get("subtitles", [])],
        )


@dataclass(slots=True)
class SceneAnalysis:
    scenes: list[SceneBoundary] = field(default_factory=list)
    has_presentation: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneAnalysis":
        raw_scenes = data.get("scenes", [])
        return cls(
            scenes=[
                SceneBoundary.from_dict(item) if isinstance(item, dict) else SceneBoundary(float(item[0]), float(item[1]))
                for item in raw_scenes
            ],
            has_presentation=bool(data.get("has_presentation", False)),
        )


@dataclass(slots=True)
class SummaryResult:
    title: str
    overview: str
    bullet_points: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SummaryResult":
        return cls(
            title=str(data["title"]),
            overview=str(data["overview"]),
            bullet_points=[str(item) for item in data.get("bullet_points", [])],
            action_items=[str(item) for item in data.get("action_items", [])],
        )

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", self.overview.strip()]
        if self.bullet_points:
            lines.extend(["", "## Highlights", ""])
            lines.extend(f"- {item}" for item in self.bullet_points)
        if self.action_items:
            lines.extend(["", "## Action Items", ""])
            lines.extend(f"- {item}" for item in self.action_items)
        return "\n".join(lines).strip() + "\n"


@dataclass(slots=True)
class ArtifactRecord:
    name: str
    path: str
    kind: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactRecord":
        return cls(name=str(data["name"]), path=str(data["path"]), kind=str(data["kind"]))


@dataclass(slots=True)
class PipelineArtifacts:
    items: dict[str, ArtifactRecord] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineArtifacts":
        raw_items = data.get("items", {})
        return cls(items={key: ArtifactRecord.from_dict(value) for key, value in raw_items.items()})


@dataclass(slots=True)
class PipelineState:
    state_version: int = 2
    input_source: Optional[InputSource] = None
    start_from: str = "prepare"
    prepared_media: Optional[PreparedMedia] = None
    asr_meta: dict[str, Any] = field(default_factory=dict)
    asr_words: list[WordToken] = field(default_factory=list)
    speaker_turns: list[SpeakerTurn] = field(default_factory=list)
    alignment: Optional[AlignmentResult] = None
    scene_analysis: Optional[SceneAnalysis] = None
    slide_segments: list[SceneSegment] = field(default_factory=list)
    summary: Optional[SummaryResult] = None
    transcript_json: Optional[str] = None
    artifacts: PipelineArtifacts = field(default_factory=PipelineArtifacts)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineState":
        if not isinstance(data, dict):
            raise TypeError("PipelineState expects a JSON object.")

        input_source: Optional[InputSource] = None
        if data.get("input_source"):
            input_source = InputSource.from_dict(data["input_source"])
        elif data.get("input_video"):
            input_source = InputSource(video_path=str(data["input_video"]), title=str(data.get("title") or ""))

        prepared_media: Optional[PreparedMedia] = None
        if data.get("prepared_media"):
            prepared_media = PreparedMedia.from_dict(data["prepared_media"])
        elif data.get("video") and data.get("duration_sec"):
            prepared_media = PreparedMedia(
                video_path=str(data.get("work_video") or ""),
                audio_path=str(data.get("audio_wav") or ""),
                metadata=MediaMetadata(
                    duration_sec=float(data["duration_sec"]),
                    width=int(data["video"]["width"]),
                    height=int(data["video"]["height"]),
                    fps=float(data["video"]["fps"]),
                ),
            )

        alignment: Optional[AlignmentResult] = None
        if data.get("alignment"):
            alignment = AlignmentResult.from_dict(data["alignment"])
        elif any(key in data for key in ("words", "utterances", "subtitles")):
            alignment = AlignmentResult(
                words=[WordToken.from_dict(item) for item in data.get("words", [])],
                utterances=[Utterance.from_dict(item) for item in data.get("utterances", [])],
                subtitles=[Utterance.from_dict(item) for item in data.get("subtitles", [])],
            )

        scene_analysis: Optional[SceneAnalysis] = None
        if data.get("scene_analysis"):
            scene_analysis = SceneAnalysis.from_dict(data["scene_analysis"])
        elif "scenes" in data or "has_presentation" in data:
            scene_analysis = SceneAnalysis.from_dict(
                {
                    "scenes": data.get("scenes", []),
                    "has_presentation": data.get("has_presentation", False),
                }
            )

        artifacts = PipelineArtifacts.from_dict(data["artifacts"]) if data.get("artifacts") else PipelineArtifacts()
        if not artifacts.items and data.get("transcript_json"):
            artifacts.items["transcript_json"] = ArtifactRecord(
                name="transcript_json",
                path=str(data["transcript_json"]),
                kind="json",
            )

        return cls(
            state_version=int(data.get("state_version", 1)),
            input_source=input_source,
            start_from=str(data.get("start_from", "prepare")),
            prepared_media=prepared_media,
            asr_meta=dict(data.get("asr_meta", {})),
            asr_words=[WordToken.from_dict(item) for item in data.get("asr_words", [])],
            speaker_turns=[SpeakerTurn.from_dict(item) for item in data.get("speaker_turns", [])],
            alignment=alignment,
            scene_analysis=scene_analysis,
            slide_segments=[SceneSegment.from_dict(item) for item in data.get("slide_segments", [])],
            summary=SummaryResult.from_dict(data["summary"]) if data.get("summary") else None,
            transcript_json=str(data["transcript_json"]) if data.get("transcript_json") else None,
            artifacts=artifacts,
        )

    def require_input_match(self, input_video: str) -> None:
        if self.input_source and self.input_source.video_path and self.input_source.video_path != input_video:
            raise RuntimeError(
                "Cannot resume pipeline with a different input video. "
                f"State is for '{self.input_source.video_path}', got '{input_video}'."
            )
