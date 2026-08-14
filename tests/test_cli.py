from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from filetree.cli import main


class CliTests(unittest.TestCase):
    def test_help_and_version_are_available(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as help_exit:
            main(["--help"])
        self.assertEqual(help_exit.exception.code, 0)
        self.assertIn("Display a directory", output.getvalue())

        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as version_exit:
            main(["--version"])
        self.assertEqual(version_exit.exception.code, 0)
        self.assertIn("filetree 0.1.0", output.getvalue())

    def test_json_output_and_success_exit_code(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "sample"
            root.mkdir()
            (root / "file.txt").touch()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main([str(root), "--json"])

        self.assertEqual(exit_code, 0)
        self.assertIn('"schema_version": 1', output.getvalue())

    def test_missing_path_returns_usage_error(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            exit_code = main(["path-that-does-not-exist"])

        self.assertEqual(exit_code, 2)
        self.assertIn("cannot access", error.getvalue())

    def test_ascii_option_uses_ascii_connectors(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "sample"
            root.mkdir()
            (root / "file.txt").touch()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main([str(root), "--ascii"])

        self.assertEqual(exit_code, 0)
        self.assertIn("`-- file.txt", output.getvalue())
