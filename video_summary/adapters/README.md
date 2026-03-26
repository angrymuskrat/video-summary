# Adapters

This directory contains concrete implementations of the interfaces defined in `video_summary.interfaces`.

It groups runtime integrations by responsibility:

- `alignment/` for word-to-speaker alignment.
- `asr/` for speech-to-text backends.
- `diarization/` for speaker attribution.
- `media/` for media preparation.
- `presentation/` for slide deck export.
- `readers/` for loading input recordings.
- `rendering/` for final video rendering.
- `scenes/` for scene detection.
- `slide_binding/` for connecting transcript segments to scenes.
- `state_store/` for saving and loading pipeline state.
- `subtitles/` for subtitle file generation.
- `summarization/` for summary generation.
- `writers/` for writing output artifacts.
