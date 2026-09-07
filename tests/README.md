# Testing boltons

Run the commands below from the repository root. For the full Python-version
matrix, see [Development](../README.md#development) and [tox.ini](../tox.ini).

## Local setup

With [uv](https://docs.astral.sh/uv/) installed, create a virtual environment
and install boltons in editable mode along with its test dependencies:

```bash
uv venv
uv pip install -e . --group dev
```

Activate it with `source .venv/bin/activate` on Unix, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell. The `python` commands below
then use that environment. Editable installation picks up local code changes
without reinstalling the package.

## Running tests

Run the tests and the examples in boltons' docstrings together:

```bash
python -m pytest --doctest-modules boltons tests
```

For a shorter feedback loop, select a file, a single test, or matching names:

```bash
python -m pytest tests/test_cacheutils.py
python -m pytest tests/test_cacheutils.py::test_lru_add
python -m pytest tests/test_cacheutils.py -k lru
```

Include a module's doctests when changing its documented behavior:

```bash
python -m pytest --doctest-modules boltons/cacheutils.py tests/test_cacheutils.py
```

Doctest comparison flags are configured in [pyproject.toml](../pyproject.toml).
CI uses tox to run both unit tests and doctests against the installed package;
the [test workflow](../.github/workflows/tests.yaml) lists the platforms and
Python versions it checks.

## Where tests belong

- `test_<module>.py` files generally mirror modules under `boltons/`; for
  example, `test_cacheutils.py` covers `boltons.cacheutils`.
- [conftest.py](conftest.py) filters version-specific test modules before
  collection. A `_py3` marker selects Python 3; a `_py37` marker selects only
  Python 3.7, not Python 3.7 and later. For example,
  `test_funcutils_fb_py3.py` contains Python-3-specific syntax.
- `jsonl_test_data.txt` and `newlines_test_data.txt` are fixtures used by
  `test_jsonutils.py` for JSON Lines and reverse line iteration. Preserve
  their contents and line endings when editing unrelated tests.

Add regression tests to the relevant module's existing test file. Use a
`test_` name that describes the behavior and confirm that the test fails
without the fix. Follow nearby tests for fixtures and parametrization;
`tmp_path` keeps filesystem tests isolated, and `pytest.raises` checks expected
exceptions. Explain non-obvious setup or edge cases in a comment or docstring.

## Coverage

Coverage is optional and requires an extra test dependency:

```bash
uv pip install pytest-cov
python -m pytest --doctest-modules boltons tests --cov=boltons --cov-config=tests/.coveragerc --cov-report=term-missing --cov-report=html
```

[.coveragerc](.coveragerc) enables branch coverage. The command prints missing
lines and writes a browsable report to `htmlcov/index.html`. Keep generated
reports out of commits.
