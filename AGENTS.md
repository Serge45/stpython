# Workspace Rules for stpython

## Development Environment
- Build System: uv / pyproject.toml
- Test Framework: pytest (run via `uv run pytest`)
- Python Version: >=3.14

## Codebase Architecture
- `stpython/`: Contains the package source code.
  - `lexer.py`: Lexer implementation converting source code into tokens.
  - `parser.py`: Parser implementation building an AST from tokens.
- `test/`: Test cases matching module patterns (e.g., `test_lexer.py`, `test_parser.py`).

## Guidelines
- Write all tests under `test/` using pytest.
- Ensure type annotations are used for all public module signatures.
- Before completing tasks, always run `uv run pytest` to ensure no regressions.
