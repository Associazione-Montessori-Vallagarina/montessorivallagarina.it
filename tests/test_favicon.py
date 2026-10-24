import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from selectolax.lexbor import LexborHTMLParser


ROOT = Path(__file__).resolve().parents[1]


class TestFavicon(unittest.TestCase):
    def test_built_pages_use_association_logo_as_favicon(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", directory],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            site = Path(directory)
            for page, source in (("index.html", "immagini/logo.png"),
                                 ("blog/2026-11/index.html", "../../immagini/logo.png")):
                with self.subTest(page=page):
                    tree = LexborHTMLParser((site / page).read_text())
                    favicon = tree.css_first('link[rel="icon"]')
                    self.assertIsNotNone(favicon)
                    self.assertEqual(favicon.attributes["href"], source)
            self.assertTrue((site / "immagini/logo.png").is_file())
