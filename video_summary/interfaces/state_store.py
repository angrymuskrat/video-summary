from __future__ import annotations

from typing import Protocol

from video_summary.domain.models import PipelineState


class StateStore(Protocol):
    def exists(self) -> bool:
        ...

    def load(self) -> PipelineState:
        ...

    def save(self, state: PipelineState) -> None:
        ...
