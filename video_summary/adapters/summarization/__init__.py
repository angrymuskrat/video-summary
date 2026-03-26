"""Package exports for the video_summary.adapters.summarization namespace."""


from .basic import BasicSummarizer
from .openai import OpenAISummarizer

__all__ = ["BasicSummarizer", "OpenAISummarizer"]
