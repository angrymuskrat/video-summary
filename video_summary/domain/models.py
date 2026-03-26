"""Domain dataclasses that capture media metadata, transcript items, artifacts, and pipeline state."""


from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class WordToken:
    """Word token.
    
    Attributes:
        start (float): Stored value for start.
        end (float): Stored value for end.
        text (str): Stored value for text.
        speaker (Optional[int]): Stored value for speaker.
    """
    start: float
    end: float
    text: str
    speaker: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WordToken":
        """Create a word token from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'WordToken': Result produced by from dict.
        """
        return cls(
            start=float(data["start"]),
            end=float(data["end"]),
            text=str(data["text"]),
            speaker=int(data["speaker"]) if data.get("speaker") is not None else None,
        )


@dataclass(slots=True)
class SpeakerTurn:
    """Speaker turn.
    
    Attributes:
        start (float): Stored value for start.
        end (float): Stored value for end.
        speaker (int): Stored value for speaker.
    """
    start: float
    end: float
    speaker: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpeakerTurn":
        """Create a speaker turn from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'SpeakerTurn': Result produced by from dict.
        """
        return cls(
            start=float(data["start"]),
            end=float(data["end"]),
            speaker=int(data["speaker"]),
        )


@dataclass(slots=True)
class Utterance:
    """Utterance.
    
    Attributes:
        start (float): Stored value for start.
        end (float): Stored value for end.
        speaker (int): Stored value for speaker.
        text (str): Stored value for text.
    """
    start: float
    end: float
    speaker: int
    text: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Utterance":
        """Create a utterance from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'Utterance': Result produced by from dict.
        """
        return cls(
            start=float(data["start"]),
            end=float(data["end"]),
            speaker=int(data["speaker"]),
            text=str(data["text"]),
        )


@dataclass(slots=True)
class SceneBoundary:
    """Scene boundary.
    
    Attributes:
        start (float): Stored value for start.
        end (float): Stored value for end.
    """
    start: float
    end: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneBoundary":
        """Create a scene boundary from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'SceneBoundary': Result produced by from dict.
        """
        return cls(start=float(data["start"]), end=float(data["end"]))


@dataclass(slots=True)
class SceneSegment:
    """Scene segment.
    
    Attributes:
        index (int): Stored value for index.
        start (float): Stored value for start.
        end (float): Stored value for end.
        frame_path (str): Stored value for frame path.
        text (str): Stored value for text.
        utterance_count (int): Stored value for utterance count.
    """
    index: int
    start: float
    end: float
    frame_path: str
    text: str
    utterance_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneSegment":
        """Create a scene segment from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'SceneSegment': Result produced by from dict.
        """
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
    """Media metadata.
    
    Attributes:
        duration_sec (float): Stored value for duration sec.
        width (int): Stored value for width.
        height (int): Stored value for height.
        fps (float): Stored value for fps.
    """
    duration_sec: float
    width: int
    height: int
    fps: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MediaMetadata":
        """Create a media metadata from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'MediaMetadata': Result produced by from dict.
        """
        return cls(
            duration_sec=float(data["duration_sec"]),
            width=int(data["width"]),
            height=int(data["height"]),
            fps=float(data["fps"]),
        )


@dataclass(slots=True)
class InputSource:
    """Input source.
    
    Attributes:
        video_path (str): Stored value for video path.
        audio_path (Optional[str]): Stored value for audio path.
        title (Optional[str]): Stored value for title.
    """
    video_path: str
    audio_path: Optional[str] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InputSource":
        """Create a input source from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'InputSource': Result produced by from dict.
        """
        return cls(
            video_path=str(data["video_path"]),
            audio_path=str(data["audio_path"]) if data.get("audio_path") else None,
            title=str(data["title"]) if data.get("title") else None,
        )


@dataclass(slots=True)
class PreparedMedia:
    """Prepared media.
    
    Attributes:
        video_path (str): Stored value for video path.
        audio_path (str): Stored value for audio path.
        metadata (MediaMetadata): Stored value for metadata.
    """
    video_path: str
    audio_path: str
    metadata: MediaMetadata

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreparedMedia":
        """Create a prepared media from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'PreparedMedia': Result produced by from dict.
        """
        return cls(
            video_path=str(data["video_path"]),
            audio_path=str(data["audio_path"]),
            metadata=MediaMetadata.from_dict(data["metadata"]),
        )


@dataclass(slots=True)
class AlignmentResult:
    """Alignment result.
    
    Attributes:
        words (list[WordToken]): Stored value for words.
        utterances (list[Utterance]): Stored value for utterances.
        subtitles (list[Utterance]): Stored value for subtitles.
    """
    words: list[WordToken] = field(default_factory=list)
    utterances: list[Utterance] = field(default_factory=list)
    subtitles: list[Utterance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AlignmentResult":
        """Create a alignment result from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'AlignmentResult': Result produced by from dict.
        """
        return cls(
            words=[WordToken.from_dict(item) for item in data.get("words", [])],
            utterances=[Utterance.from_dict(item) for item in data.get("utterances", [])],
            subtitles=[Utterance.from_dict(item) for item in data.get("subtitles", [])],
        )


@dataclass(slots=True)
class SceneAnalysis:
    """Scene analysis.
    
    Attributes:
        scenes (list[SceneBoundary]): Stored value for scenes.
        has_presentation (bool): Stored value for has presentation.
    """
    scenes: list[SceneBoundary] = field(default_factory=list)
    has_presentation: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneAnalysis":
        """Create a scene analysis from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'SceneAnalysis': Result produced by from dict.
        """
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
    """Summary result.
    
    Attributes:
        title (str): Stored value for title.
        overview (str): Stored value for overview.
        bullet_points (list[str]): Stored value for bullet points.
        action_items (list[str]): Stored value for action items.
    """
    title: str
    overview: str
    bullet_points: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SummaryResult":
        """Create a summary result from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'SummaryResult': Result produced by from dict.
        """
        return cls(
            title=str(data["title"]),
            overview=str(data["overview"]),
            bullet_points=[str(item) for item in data.get("bullet_points", [])],
            action_items=[str(item) for item in data.get("action_items", [])],
        )

    def to_markdown(self) -> str:
        """To markdown.
        
        Returns:
            str: Result produced by to markdown.
        """
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
    """Artifact record.
    
    Attributes:
        name (str): Stored value for name.
        path (str): Stored value for path.
        kind (str): Stored value for kind.
    """
    name: str
    path: str
    kind: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactRecord":
        """Create a artifact record from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'ArtifactRecord': Result produced by from dict.
        """
        return cls(name=str(data["name"]), path=str(data["path"]), kind=str(data["kind"]))


@dataclass(slots=True)
class PipelineArtifacts:
    """Pipeline artifacts.
    
    Attributes:
        items (dict[str, ArtifactRecord]): Stored value for items.
    """
    items: dict[str, ArtifactRecord] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineArtifacts":
        """Create a pipeline artifacts from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'PipelineArtifacts': Result produced by from dict.
        """
        raw_items = data.get("items", {})
        return cls(items={key: ArtifactRecord.from_dict(value) for key, value in raw_items.items()})


@dataclass(slots=True)
class PipelineState:
    """Pipeline state.
    
    Attributes:
        state_version (int): Stored value for state version.
        input_source (Optional[InputSource]): Stored value for input source.
        start_from (str): Stored value for start from.
        prepared_media (Optional[PreparedMedia]): Stored value for prepared media.
        asr_meta (dict[str, Any]): Stored value for asr meta.
        asr_words (list[WordToken]): Stored value for asr words.
        speaker_turns (list[SpeakerTurn]): Stored value for speaker turns.
        alignment (Optional[AlignmentResult]): Stored value for alignment.
        scene_analysis (Optional[SceneAnalysis]): Stored value for scene analysis.
        slide_segments (list[SceneSegment]): Stored value for slide segments.
        summary (Optional[SummaryResult]): Stored value for summary.
        transcript_json (Optional[str]): Stored value for transcript json.
        artifacts (PipelineArtifacts): Stored value for artifacts.
    """
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
        """To dict.
        
        Returns:
            dict[str, Any]: Result produced by to dict.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineState":
        """Create a pipeline state from dict.
        
        Args:
            data (dict[str, Any]): Value for data.
        
        Returns:
            'PipelineState': Result produced by from dict.
        """
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
        """Return the required input match.
        
        Args:
            input_video (str): Value for input video.
        """
        if self.input_source and self.input_source.video_path and self.input_source.video_path != input_video:
            raise RuntimeError(
                "Cannot resume pipeline with a different input video. "
                f"State is for '{self.input_source.video_path}', got '{input_video}'."
            )
