from __future__ import annotations

from typing import Optional, Sequence

from video_summary.cli import config_from_args, parse_args
from video_summary.orchestrator import build_default_pipeline


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    pipeline = build_default_pipeline(config_from_args(args))
    pipeline.run()
    return 0
