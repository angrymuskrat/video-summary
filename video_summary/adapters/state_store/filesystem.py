from __future__ import annotations

import json

from video_summary.config import PipelineConfig
from video_summary.domain.models import PipelineState


class FilesystemStateStore:
    def __init__(self, config: PipelineConfig) -> None:
        self._path = config.layout().state_path

    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> PipelineState:
        if not self._path.exists():
            raise FileNotFoundError(
                f"State file '{self._path}' is missing. Run a full pipeline first or restart from 'prepare'."
            )
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return PipelineState.from_dict(data)

    def save(self, state: PipelineState) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
