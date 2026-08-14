"""Filesystem-tree data structures independent of any output format."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class NodeKind(StrEnum):
    """The kind of a filesystem entry represented by a tree node."""

    DIRECTORY = "directory"
    FILE = "file"
    SYMLINK = "symlink"
    OTHER = "other"


@dataclass(slots=True)
class TreeNode:
    """One visible filesystem entry and, for directories, its visible children."""

    name: str
    kind: NodeKind
    children: list[TreeNode] = field(default_factory=list)
    error: str | None = None
    target: str | None = None


@dataclass(slots=True)
class TreeStats:
    """Counts of nodes included in the rendered tree."""

    directories: int = 0
    files: int = 0
    symlinks: int = 0
    other: int = 0

    def add(self, kind: NodeKind) -> None:
        """Record one visible node of *kind*."""
        match kind:
            case NodeKind.DIRECTORY:
                self.directories += 1
            case NodeKind.FILE:
                self.files += 1
            case NodeKind.SYMLINK:
                self.symlinks += 1
            case NodeKind.OTHER:
                self.other += 1


@dataclass(slots=True)
class TreeResult:
    """A tree traversal result, including displayed-node statistics."""

    root: TreeNode
    stats: TreeStats
