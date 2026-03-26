"""Package exports for the video_summary.adapters.readers namespace."""


from .database import DatabaseInputReader
from .filesystem import FilesystemInputReader

__all__ = ["DatabaseInputReader", "FilesystemInputReader"]
