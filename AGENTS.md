# AGENTS.md

This file provides guidance to agents when working with code in this repository.

- The project contains multiple independent parametric CAD modules using [`build123d`](src/build123d/pyproject.toml:1) and custom assemblies in [`workboard/projects/`](workboard/projects/).
- Each module (e.g., `easel`, `pizzapancoolingmat`) has its own props/config, CLI, and test files. CLI argument schemas are generated dynamically from Pydantic models ([`schemas.py`](workboard/projects/pizzapancoolingmat/schemas.py:1)), not hardcoded.
- To run a single module's CLI:  
  `python -m workboard.projects.<module>.main --help`  
  (e.g., `python -m workboard.projects.pizzapancoolingmat.main --list-props`)
- To run all tests for a module:  
  `pytest workboard/projects/<module>/`  
  (e.g., `pytest workboard/projects/pizzapancoolingmat/`)
- To run all tests for build123d:  
  `pytest src/build123d/tests/`
- Some modules require the `ocp_vscode` extension for 3D visualization in VSCode; headless runs will print geometry objects.
- Test files may use subprocess to invoke CLI scripts and validate CLI output, not just direct Python calls ([`test_main.py`](workboard/projects/pizzapancoolingmat/test_main.py:1)).
- CLI argument defaults and help text are generated from Pydantic model fields, including units and required status.
- Custom test helpers are defined in each module's test files (e.g., label-based part lookup in [`test_easel.py`](workboard/projects/easel/test_easel.py:1)).
- Code style:  
  - Black formatting, line length 88 ([`pyproject.toml`](pyproject.toml:49), [`src/build123d/pyproject.toml`](src/build123d/pyproject.toml:107))
  - Type hints required for all public APIs; mypy ignores missing imports for many CAD dependencies ([`src/build123d/mypy.ini`](src/build123d/mypy.ini:1))
  - Imports may be grouped by CAD library, standard lib, and project modules, but not strictly enforced.
- Non-obvious:  
  - Each module's CLI dynamically exposes all Pydantic model fields as CLI args, including units and required/optional status.
  - Some test scripts expect CLI errors for invalid/missing arguments and check for specific error messages in stdout/stderr.
  - The `workboard` package uses `pyproject.toml` for both build and test dependencies; some scripts are only available via `[project.scripts]`.
  - `build123d`'s own tests dynamically generate tests for all example scripts by scanning the examples directory ([`test_examples.py`](src/build123d/tests/test_examples.py:1)).
  - Some modules (e.g., `pizzapancoolingmat`) use multiple fallback imports for Pydantic internals to support different Pydantic versions.
