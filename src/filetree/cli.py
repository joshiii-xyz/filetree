"""Command-line interface for filetree."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from filetree import __version__
from filetree.render import render_json, render_text
from filetree.traversal import TraversalError, TraversalOptions, build_tree


def _non_negative_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser, kept separate for direct behavioral tests."""
    parser = argparse.ArgumentParser(
        prog="filetree",
        description="Display a directory as a readable, deterministic tree.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="directory or file to display (default: current directory)",
    )
    parser.add_argument(
        "-d",
        "--depth",
        metavar="N",
        type=_non_negative_integer,
        help="maximum levels below the root to display",
    )
    parser.add_argument(
        "-a", "--hidden", action="store_true", help="include entries whose names begin with a dot"
    )
    parser.add_argument(
        "-I",
        "--exclude",
        metavar="PATTERN",
        action="append",
        default=[],
        help="exclude a shell-style name or relative-path pattern; repeatable",
    )
    parser.add_argument(
        "--json", action="store_true", help="write the structured JSON representation"
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="use ASCII connectors instead of Unicode tree characters",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run filetree and return its process exit status."""
    args = build_parser().parse_args(argv)
    options = TraversalOptions(
        max_depth=args.depth,
        include_hidden=args.hidden,
        exclude_patterns=tuple(args.exclude),
    )
    try:
        result = build_tree(args.path, options)
    except TraversalError as error:
        print(f"filetree: error: {error}", file=sys.stderr)
        return 2

    stdout_supports_unicode = _stdout_supports_unicode()
    use_unicode = not args.ascii and stdout_supports_unicode
    output = (
        render_json(result, ensure_ascii=not stdout_supports_unicode)
        if args.json
        else render_text(result, unicode=use_unicode)
    )
    _write_output(output)
    return 0


def _stdout_supports_unicode() -> bool:
    """Return whether the active stdout encoding can represent tree glyphs."""
    encoding = sys.stdout.encoding
    if encoding is None:
        return True
    try:
        "├── ".encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


def _write_output(output: str) -> None:
    """Write output without failing on filenames outside a legacy console encoding."""
    encoding = sys.stdout.encoding
    if encoding is not None:
        output = output.encode(encoding, errors="backslashreplace").decode(encoding)
    print(output, end="")


if __name__ == "__main__":
    raise SystemExit(main())
