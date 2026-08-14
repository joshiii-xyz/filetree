from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from filetree.model import NodeKind
from filetree.traversal import TraversalError, TraversalOptions, build_tree


class TraversalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "project"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_builds_deterministic_directory_first_tree_and_statistics(self) -> None:
        (self.root / "z-file.txt").touch()
        (self.root / "alpha").mkdir()
        (self.root / "alpha" / "nested.py").touch()
        (self.root / "Beta").mkdir()
        (self.root / "a-file.txt").touch()

        result = build_tree(self.root, TraversalOptions())

        self.assertEqual(
            [child.name for child in result.root.children],
            ["alpha", "Beta", "a-file.txt", "z-file.txt"],
        )
        self.assertEqual(result.stats.directories, 3)
        self.assertEqual(result.stats.files, 3)

    def test_depth_zero_keeps_only_root_and_depth_one_keeps_direct_children(self) -> None:
        (self.root / "directory").mkdir()
        (self.root / "directory" / "child.txt").touch()

        root_only = build_tree(self.root, TraversalOptions(max_depth=0))
        depth_one = build_tree(self.root, TraversalOptions(max_depth=1))

        self.assertEqual(root_only.root.children, [])
        self.assertEqual([child.name for child in depth_one.root.children], ["directory"])
        self.assertEqual(depth_one.root.children[0].children, [])

    def test_hidden_entries_are_omitted_unless_requested(self) -> None:
        (self.root / ".private").mkdir()
        (self.root / ".private" / "secret").touch()
        (self.root / "visible").touch()

        default = build_tree(self.root, TraversalOptions())
        including_hidden = build_tree(self.root, TraversalOptions(include_hidden=True))

        self.assertEqual([child.name for child in default.root.children], ["visible"])
        self.assertEqual(
            [child.name for child in including_hidden.root.children], [".private", "visible"]
        )

    def test_exclusions_match_names_and_relative_paths(self) -> None:
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "package.json").touch()
        (self.root / "src").mkdir()
        (self.root / "src" / "generated").mkdir()
        (self.root / "src" / "generated" / "api.py").touch()
        (self.root / "src" / "main.py").touch()

        result = build_tree(
            self.root,
            TraversalOptions(exclude_patterns=("node_modules", "src/generated")),
        )

        self.assertEqual([child.name for child in result.root.children], ["src"])
        self.assertEqual([child.name for child in result.root.children[0].children], ["main.py"])

    def test_supports_unicode_and_spaces(self) -> None:
        (self.root / "résumé notes.txt").touch()

        result = build_tree(self.root, TraversalOptions())

        self.assertEqual(result.root.children[0].name, "résumé notes.txt")

    def test_does_not_follow_symlink_directories(self) -> None:
        target = self.root / "target"
        target.mkdir()
        (target / "inside.txt").touch()
        link = self.root / "link"
        try:
            os.symlink(target, link, target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"symlinks unavailable: {error}")

        result = build_tree(self.root, TraversalOptions())
        linked = next(node for node in result.root.children if node.name == "link")

        self.assertEqual(linked.kind, NodeKind.SYMLINK)
        self.assertEqual(linked.children, [])
        self.assertEqual(result.stats.symlinks, 1)

    def test_invalid_root_raises_a_clear_error(self) -> None:
        with self.assertRaisesRegex(TraversalError, "cannot access"):
            build_tree(self.root / "missing", TraversalOptions())

    def test_permission_error_on_directory_is_reported_on_its_node(self) -> None:
        with patch("filetree.traversal.os.scandir", side_effect=PermissionError("denied")):
            result = build_tree(self.root, TraversalOptions())

        self.assertEqual(result.root.error, "permission denied")
