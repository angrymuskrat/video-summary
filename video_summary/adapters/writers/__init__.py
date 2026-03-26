"""Package exports for the video_summary.adapters.writers namespace."""


from .database import DatabaseArtifactWriter
from .filesystem import FilesystemArtifactWriter

__all__ = ["DatabaseArtifactWriter", "FilesystemArtifactWriter"]
