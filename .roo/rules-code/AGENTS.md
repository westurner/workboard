# Project Coding Rules (Non-Obvious Only)

- Each module's CLI dynamically generates all CLI arguments from Pydantic models; do not hardcode argument parsing.
- Test helpers for part lookup by label are required for geometry assertions (see [`test_easel.py`](workboard/projects/easel/test_easel.py:1)).
- Some modules use fallback imports for Pydantic internals to support multiple Pydantic versions ([`main.py`](workboard/projects/pizzapancoolingmat/main.py:11)).
- CLI argument units and required/optional status are surfaced from Pydantic field metadata.
- Imports may be grouped by CAD library, standard lib, and project modules, but this is not strictly enforced by linters.