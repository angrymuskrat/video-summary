# Interfaces

This directory defines the protocol layer for the library.

Each module describes one replaceable pipeline capability, such as input loading, media preparation, ASR, diarization, subtitle generation, artifact writing, or state persistence. Adapters implement these protocols, and the orchestrator depends on them instead of concrete providers.
