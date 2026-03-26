"""Core package exports and runtime entrypoints for the video summary library."""


from .cli import build_parser, config_from_args, parse_args
from .config import OutputLayout, PipelineConfig, STEP_ORDER
from .orchestrator import MeetingPipeline, build_default_pipeline

__all__ = [
    "MeetingPipeline",
    "OutputLayout",
    "PipelineConfig",
    "STEP_ORDER",
    "build_default_pipeline",
    "build_parser",
    "config_from_args",
    "parse_args",
]
