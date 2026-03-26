"""Tests for cli behavior in the video summary package."""


from video_summary.cli import config_from_args, parse_args


def test_cli_parser_keeps_legacy_arguments() -> None:
    """Test that cli parser keeps legacy arguments."""
    args = parse_args(
        [
            "--input",
            "meeting.webm",
            "--output-dir",
            "out",
            "--hf-token",
            "token",
            "--language",
            "ru",
            "--model",
            "large-v3",
            "--device",
            "cpu",
            "--compute-type",
            "int8",
            "--ffmpeg-video-encoder",
            "libx264",
            "--presentation",
            "yes",
            "--scene-detector",
            "hash",
            "--scene-threshold",
            "0.2",
            "--min-scene-sec",
            "7",
            "--num-speakers",
            "2",
            "--min-speakers",
            "1",
            "--max-speakers",
            "3",
            "--subtitle-max-chars",
            "90",
            "--subtitle-max-duration",
            "5.5",
            "--transcript-gap",
            "0.9",
            "--start-from",
            "align",
            "--export-pdf",
            "--keep-work-files",
        ]
    )

    config = config_from_args(args)

    assert config.language == "ru"
    assert config.presentation == "yes"
    assert config.start_from == "align"
    assert config.export_pdf is True
    assert config.keep_work_files is True
