from __future__ import annotations

import json
import unittest

from filetree.model import NodeKind, TreeNode, TreeResult, TreeStats
from filetree.render import render_json, render_text


class RenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = TreeResult(
            TreeNode(
                "project",
                NodeKind.DIRECTORY,
                children=[
                    TreeNode(
                        "src", NodeKind.DIRECTORY, children=[TreeNode("main.py", NodeKind.FILE)]
                    ),
                    TreeNode("README.md", NodeKind.FILE),
                ],
            ),
            TreeStats(directories=2, files=2),
        )

    def test_unicode_text_tree_and_summary(self) -> None:
        self.assertEqual(
            render_text(self.result),
            "project/\n├── src/\n│   └── main.py\n└── README.md\n\n2 directories, 2 files",
        )

    def test_json_is_structured_and_stable(self) -> None:
        document = json.loads(render_json(self.result))

        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(document["root"]["children"][0]["type"], "directory")
        self.assertEqual(
            document["statistics"], {"directories": 2, "files": 2, "symlinks": 0, "other": 0}
        )
