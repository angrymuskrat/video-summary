from __future__ import annotations

from video_summary.config import PipelineConfig
from video_summary.domain.models import InputSource


class DatabaseInputReader:
    def load(self, config: PipelineConfig) -> InputSource:
        raise NotImplementedError(
            "DatabaseInputReader is a contract placeholder. "
            "Add a DB-backed lookup here without changing the orchestrator."
        )
