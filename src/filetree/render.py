"""Human and JSON renderers for filetree's internal tree model."""

from __future__ import annotations

import json

from filetree.model import NodeKind, TreeNode, TreeResult


def render_text(result: TreeResult, *, unicode: bool = True) -> str:
    """Render a ``TreeResult`` as a compact, readable directory tree."""
    branch, last_branch, vertical, space = (
        ("├── ", "└── ", "│   ", "    ") if unicode else ("|-- ", "`-- ", "|   ", "    ")
    )
    lines = [_node_label(result.root)]

    def visit(node: TreeNode, prefix: str) -> None:
        for index, child in enumerate(node.children):
            is_last = index == len(node.children) - 1
            lines.append(f"{prefix}{last_branch if is_last else branch}{_node_label(child)}")
            visit(child, f"{prefix}{space if is_last else vertical}")

    visit(result.root, "")
    lines.extend(("", _summary(result)))
    return "\n".join(lines)


def render_json(result: TreeResult, *, indent: int | None = 2, ensure_ascii: bool = False) -> str:
    """Render a stable, structured JSON document rather than terminal text."""
    document = {
        "schema_version": 1,
        "root": _node_json(result.root),
        "statistics": {
            "directories": result.stats.directories,
            "files": result.stats.files,
            "symlinks": result.stats.symlinks,
            "other": result.stats.other,
        },
    }
    return json.dumps(document, ensure_ascii=ensure_ascii, indent=indent) + "\n"


def _node_label(node: TreeNode) -> str:
    label = node.name
    if node.kind == NodeKind.DIRECTORY:
        label += "/"
    elif node.kind == NodeKind.SYMLINK and node.target is not None:
        label += f" -> {node.target}"
    if node.error:
        label += f" [{node.error}]"
    return label


def _summary(result: TreeResult) -> str:
    stats = result.stats
    pieces = [_count(stats.directories, "directory"), _count(stats.files, "file")]
    if stats.symlinks:
        pieces.append(_count(stats.symlinks, "symlink"))
    if stats.other:
        pieces.append(_count(stats.other, "other"))
    return ", ".join(pieces)


def _count(value: int, noun: str) -> str:
    plural = "directories" if noun == "directory" else f"{noun}s"
    return f"{value} {noun if value == 1 else plural}"


def _node_json(node: TreeNode) -> dict[str, object]:
    value: dict[str, object] = {"name": node.name, "type": node.kind.value}
    if node.target is not None:
        value["target"] = node.target
    if node.error is not None:
        value["error"] = node.error
    if node.kind == NodeKind.DIRECTORY:
        value["children"] = [_node_json(child) for child in node.children]
    return value
