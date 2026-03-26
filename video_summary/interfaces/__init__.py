"""Protocol definitions for pluggable pipeline components."""


from .alignment import AlignmentEngine
from .asr import ASREngine
from .diarization import DiarizationEngine
from .media import MediaPreparator
from .presentation import PresentationGenerator
from .readers import InputReader
from .rendering import VideoRenderer
from .scenes import SceneDetector
from .slide_binding import SlideBinder
from .state_store import StateStore
from .subtitles import SubtitleGenerator
from .summarization import Summarizer
from .writers import ArtifactWriter

__all__ = [
    "ASREngine",
    "AlignmentEngine",
    "ArtifactWriter",
    "DiarizationEngine",
    "InputReader",
    "MediaPreparator",
    "PresentationGenerator",
    "SceneDetector",
    "SlideBinder",
    "StateStore",
    "SubtitleGenerator",
    "Summarizer",
    "VideoRenderer",
]
