# Contributing

## Development setup

Use Python 3.11 or newer. Create an isolated environment if preferred, then install the project and development checks:

```console
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Keep changes focused and add deterministic tests for behavior changes. Filesystem tests must use temporary fixtures rather than the checkout. Avoid platform assumptions: Windows, macOS, and Linux are supported.

## Pull requests

Explain the user-visible change, include test coverage, and keep documentation in sync with CLI or JSON-schema changes. Please do not add runtime dependencies without explaining the cross-platform or maintenance benefit.

## Releases

Versions follow semantic versioning. Update `CHANGELOG.md` and `src/filetree/__init__.py` together for a release. Releases are built from a tagged commit and published as Python wheels and source distributions.
