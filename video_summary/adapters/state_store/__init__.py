"""Package exports for the video_summary.adapters.state_store namespace."""


from .database import DatabaseStateStore
from .filesystem import FilesystemStateStore

__all__ = ["DatabaseStateStore", "FilesystemStateStore"]
