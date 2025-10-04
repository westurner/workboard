# Project Architecture Rules (Non-Obvious Only)

- Each CAD module is fully independent, with its own CLI, config, and test suite.
- CLI argument schemas are always generated from Pydantic models; never duplicated or hardcoded.
- Test discovery for `build123d` examples is dynamic—new scripts are automatically tested ([`test_examples.py`](src/build123d/tests/test_examples.py:1)).
- Some modules use fallback imports to support multiple Pydantic versions ([`main.py`](workboard/projects/pizzapancoolingmat/main.py:11)).