"""Safe, deterministic filesystem traversal for filetree."""

from __future__ import annotations

import fnmatch
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from filetree.model import NodeKind, TreeNode, TreeResult, TreeStats


class TraversalError(Exception):
    """A failure that prevents constructing a tree for the requested root."""


@dataclass(frozen=True, slots=True)
class TraversalOptions:
    """Controls for one traversal.

    ``max_depth`` counts levels below the supplied root; zero displays only the root.
    Exclusion patterns are shell-style patterns matched against both a basename and a
    slash-separated relative path.
    """

    max_depth: int | None = None
    include_hidden: bool = False
    exclude_patterns: tuple[str, ...] = ()


def build_tree(path: Path, options: TraversalOptions) -> TreeResult:
    """Build a visible tree rooted at *path* without recursively following symlinks."""
    try:
        root_stat = path.lstat()
    except OSError as error:
        raise TraversalError(_root_error(path, error)) from error

    root_kind = _kind_from_mode(root_stat.st_mode)
    root = TreeNode(_display_name(path), root_kind, target=_symlink_target(path, root_kind))
    stats = TreeStats()
    stats.add(root_kind)
    if root_kind == NodeKind.DIRECTORY:
        _populate_directory(path, root, 0, Path(), options, stats)
    return TreeResult(root, stats)


def _populate_directory(
    path: Path,
    node: TreeNode,
    depth: int,
    relative_path: Path,
    options: TraversalOptions,
    stats: TreeStats,
) -> None:
    if options.max_depth is not None and depth >= options.max_depth:
        return
    try:
        with os.scandir(path) as entries:
            visible_entries = [
                entry for entry in entries if _include_entry(entry.name, relative_path, options)
            ]
    except OSError as error:
        node.error = _entry_error(error)
        return

    visible_entries.sort(key=_entry_sort_key)
    for entry in visible_entries:
        child_path = path / entry.name
        child_relative_path = relative_path / entry.name
        try:
            entry_stat = entry.stat(follow_symlinks=False)
        except OSError as error:
            node.children.append(TreeNode(entry.name, NodeKind.OTHER, error=_entry_error(error)))
            stats.add(NodeKind.OTHER)
            continue

        kind = _kind_from_mode(entry_stat.st_mode)
        child = TreeNode(entry.name, kind, target=_symlink_target(child_path, kind))
        node.children.append(child)
        stats.add(kind)
        if kind == NodeKind.DIRECTORY:
            _populate_directory(child_path, child, depth + 1, child_relative_path, options, stats)


def _include_entry(name: str, parent: Path, options: TraversalOptions) -> bool:
    if not options.include_hidden and name.startswith("."):
        return False
    relative = (parent / name).as_posix()
    return not any(
        fnmatch.fnmatchcase(name, pattern) or fnmatch.fnmatchcase(relative, pattern)
        for pattern in options.exclude_patterns
    )


def _entry_sort_key(entry: os.DirEntry[str]) -> tuple[int, str, str]:
    try:
        is_directory = entry.is_dir(follow_symlinks=False)
    except OSError:
        is_directory = False
    return (0 if is_directory else 1, entry.name.casefold(), entry.name)


def _kind_from_mode(mode: int) -> NodeKind:
    if stat.S_ISDIR(mode):
        return NodeKind.DIRECTORY
    if stat.S_ISREG(mode):
        return NodeKind.FILE
    if stat.S_ISLNK(mode):
        return NodeKind.SYMLINK
    return NodeKind.OTHER


def _symlink_target(path: Path, kind: NodeKind) -> str | None:
    if kind != NodeKind.SYMLINK:
        return None
    try:
        return os.readlink(path)
    except OSError:
        return None


def _display_name(path: Path) -> str:
    try:
        return path.resolve(strict=False).name or str(path)
    except OSError:
        return path.name or str(path)


def _root_error(path: Path, error: OSError) -> str:
    return f"cannot access {path!s}: {_entry_error(error)}"


def _entry_error(error: OSError) -> str:
    if isinstance(error, PermissionError):
        return "permission denied"
    return error.strerror or "filesystem error"
