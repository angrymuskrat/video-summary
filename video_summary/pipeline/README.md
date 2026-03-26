# Pipeline

This directory contains the runtime structures that drive execution of the processing flow.

- `context.py` holds the shared execution context and accumulated pipeline state.
- `steps/` contains the ordered step implementations used by the orchestrator.

The orchestrator builds a `PipelineContext`, then runs the enabled steps in sequence starting from the configured checkpoint.
