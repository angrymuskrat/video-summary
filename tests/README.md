# Tests

This directory contains the automated test suite for the repository.

The tests primarily exercise:

- CLI parsing and configuration assembly.
- Domain model behavior and validation.
- Filesystem-backed adapters.
- Orchestrator flow using fake adapters.
- Transcript, summarization, and slide-mapping helper services.

The suite is intended to stay lightweight and deterministic, so it uses temporary directories, fakes, and generated files instead of real ML backends.
