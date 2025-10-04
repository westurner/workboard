# Project Debug Rules (Non-Obvious Only)

- Some test scripts invoke CLI via subprocess and expect specific error messages in stderr/stdout (see [`test_main.py`](workboard/projects/pizzapancoolingmat/test_main.py:1)).
- 3D visualization in VSCode requires the `ocp_vscode` extension; headless runs print geometry objects.
- `build123d` example tests dynamically generate test cases for all scripts in the examples directory ([`test_examples.py`](src/build123d/tests/test_examples.py:1)).