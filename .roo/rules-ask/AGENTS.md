# Project Documentation Rules (Non-Obvious Only)

- Each module's CLI help and argument schema is generated from Pydantic models, not static docs.
- Some test helpers and CLI usage patterns are only documented in test files (see [`test_easel.py`](workboard/projects/easel/test_easel.py:1), [`test_main.py`](workboard/projects/pizzapancoolingmat/test_main.py:1)).
- Example scripts for `build123d` are the canonical reference for usage and are tested automatically ([`test_examples.py`](src/build123d/tests/test_examples.py:1)).