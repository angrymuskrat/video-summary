from __future__ import annotations

from video_summary.domain.models import PipelineState


class DatabaseStateStore:
    def exists(self) -> bool:
        raise NotImplementedError(
            "DatabaseStateStore is a contract placeholder. "
            "Add DB-backed state persistence here without changing the orchestrator."
        )

    def load(self) -> PipelineState:
        raise NotImplementedError(
            "DatabaseStateStore is a contract placeholder. "
            "Add DB-backed state persistence here without changing the orchestrator."
        )

    def save(self, state: PipelineState) -> None:
        raise NotImplementedError(
            "DatabaseStateStore is a contract placeholder. "
            "Add DB-backed state persistence here without changing the orchestrator."
        )
