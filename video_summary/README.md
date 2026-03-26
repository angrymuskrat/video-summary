# video_summary Package

This package contains the public library surface and the code that wires the meeting-processing pipeline together.

Main modules:

- `cli.py` builds and parses command-line arguments.
- `config.py` defines runtime configuration and output layout models.
- `main.py` exposes the executable package entrypoint.
- `orchestrator.py` assembles the pipeline and its default adapters.

Subpackages:

- `adapters/` contains concrete implementations for external tools and persistence layers.
- `domain/` contains shared dataclasses used across the pipeline.
- `interfaces/` contains protocols that make adapters replaceable.
- `pipeline/` contains execution context and step-level flow control.
- `services/` contains pure helper logic that is reusable across adapters and steps.
