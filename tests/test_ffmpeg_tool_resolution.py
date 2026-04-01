"""Tests for resilient ffmpeg/ffprobe binary resolution."""


from __future__ import annotations

from video_summary.adapters.media import ffmpeg as ffmpeg_module


def test_resolve_tool_prefers_explicit_environment_override(monkeypatch, tmp_path) -> None:
    """An explicit env var should win even when PATH lookup fails."""
    binary = tmp_path / "ffmpeg"
    binary.write_text("", encoding="utf-8")

    monkeypatch.setenv("VIDEO_SUMMARY_FFMPEG_BIN", str(binary))
    monkeypatch.setattr(ffmpeg_module.shutil, "which", lambda _name: None)

    assert ffmpeg_module.resolve_tool("ffmpeg") == str(binary)


def test_resolve_tool_uses_common_absolute_fallback_paths(monkeypatch) -> None:
    """A known absolute install path should be accepted when PATH is incomplete."""
    fallback = "/usr/bin/ffmpeg"

    monkeypatch.delenv("VIDEO_SUMMARY_FFMPEG_BIN", raising=False)
    monkeypatch.setattr(ffmpeg_module.shutil, "which", lambda _name: None)
    monkeypatch.setattr(ffmpeg_module, "TOOL_FALLBACK_PATHS", {"ffmpeg": (fallback,), "ffprobe": ()})
    monkeypatch.setattr(ffmpeg_module, "path_exists", lambda path: path == fallback)

    assert ffmpeg_module.resolve_tool("ffmpeg") == fallback


def test_run_command_uses_resolved_binary_path(monkeypatch) -> None:
    """All subprocess invocations should use the resolved executable path."""
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(list(cmd))
        return object()

    monkeypatch.setattr(ffmpeg_module, "resolve_tool", lambda name: f"/resolved/{name}")
    monkeypatch.setattr(ffmpeg_module.subprocess, "run", fake_run)

    ffmpeg_module.run_command(["ffmpeg", "-version"])

    assert calls == [["/resolved/ffmpeg", "-version"]]
