import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mkdocs.config.defaults import MkDocsConfig
from selectolax.lexbor import LexborHTMLParser

from version import on_config


ROOT = Path(__file__).resolve().parents[1]


class TestVersion(unittest.TestCase):
    @patch("version.subprocess.run")
    def test_footer_uses_repository_commit(self, mock_run: MagicMock) -> None:
        config = MagicMock(spec=MkDocsConfig)
        config.config_file_path = str(ROOT / "mkdocs.yml")
        mock_run.return_value.stdout = "abc1234\n"

        self.assertIs(on_config(config), config)
        self.assertEqual(config.copyright, "<small>abc1234</small>")
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_built_pages_show_commit_in_footer(self) -> None:
        commit_id = subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", directory],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            for page in ["index.html", "scuola-infanzia-rovereto/index.html"]:
                tree = LexborHTMLParser((Path(directory) / page).read_text())
                version = tree.css_first("footer .md-copyright__highlight small")
                self.assertIsNotNone(version)
                self.assertEqual(version.text(), commit_id)
                self.assertIsNone(version.css_first("code"))
