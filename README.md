# filetree

[![CI](https://github.com/joshiii-xyz/filetree/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/joshiii-xyz/filetree/actions/workflows/ci.yml)

`filetree` is a fast, readable, cross-platform CLI for showing a filesystem path as a tree. It is intentionally small, read-only, and useful out of the box for developer repositories.

**Highlights:** deterministic ordering · zero runtime dependencies · safe symlink handling · Unicode or ASCII output · structured JSON

```text
$ filetree .
my-project/
├── src/
│   ├── config.py
│   ├── main.py
│   └── utils/
│       └── parser.py
├── tests/
│   └── test_parser.py
├── pyproject.toml
└── README.md

4 directories, 5 files
```

## Install

Requires Python 3.11 or newer.

```console
python -m pip install filetree
filetree --help
```

For an isolated CLI installation, [`pipx`](https://pipx.pypa.io/) is also a good fit:

```console
pipx install filetree
```

For a checkout, install an editable development copy:

```console
python -m pip install -e .
```

## Usage

```console
filetree [PATH] [OPTIONS]
```

`PATH` defaults to the current directory. Directories appear before files and names are sorted deterministically, case-insensitively with a case-sensitive tie-breaker.

| Option | Description |
| --- | --- |
| `-d N`, `--depth N` | Show at most `N` levels below the root. `0` shows only the root. |
| `-a`, `--hidden` | Include names beginning with `.`. |
| `-I PATTERN`, `--exclude PATTERN` | Exclude a shell-style basename or slash-separated relative-path pattern. Repeatable. |
| `--json` | Write structured JSON instead of a terminal tree. |
| `--ascii` | Use ASCII connectors for terminals that cannot display Unicode. |
| `--version` | Print the installed version. |

Examples:

```console
# Inspect the current project, stopping after two child levels.
filetree --depth 2

# Include dotfiles but leave build output and VCS metadata out.
filetree . --hidden --exclude .git --exclude node_modules --exclude dist

# Feed a structured tree to another tool.
filetree ./service --json
```

## Behavior and safety

`filetree` never writes to, deletes, or executes filesystem entries. It does not recursively follow symbolic links, preventing cycles. Links are shown as `name -> target`; broken links are still displayed when their link itself is readable.

Unreadable directories remain visible and are annotated with `[permission denied]` where the operating system exposes that error. An inaccessible root path prints a clear error to stderr and exits with status `2`; successful inspections exit `0`. Argument parsing errors also exit `2`.

Hidden entries are names beginning with `.`, consistently on every platform. Exclusion patterns use Python shell-style matching and are tested against both an entry name and its slash-separated path relative to the supplied root. Excluded entries are not displayed or counted.

## JSON schema

`--json` emits a stable JSON document rather than serialized terminal output:

```json
{
  "schema_version": 1,
  "root": {
    "name": "service",
    "type": "directory",
    "children": []
  },
  "statistics": {
    "directories": 1,
    "files": 0,
    "symlinks": 0,
    "other": 0
  }
}
```

Node types are `directory`, `file`, `symlink`, or `other`. Directory nodes always include `children`; symlinks may include `target`; entries that could not be read may include `error`. Counts cover the nodes visible in the response, including the root.

## Development

```console
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
python -m mypy src
```

The project uses only the Python standard library at runtime. `ruff` is a development-only dependency used to keep formatting and common correctness checks consistent. See [architecture.md](docs/architecture.md) for the component boundaries.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change. Bug reports and small, focused improvements are welcome. For the release process and compatibility policy, see [CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
