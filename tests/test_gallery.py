import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from selectolax.lexbor import LexborHTMLParser

from gallery import _gallery_html


ROOT = Path(__file__).resolve().parents[1]


class TestGallery(unittest.TestCase):
    def test_thumbnail_columns_stay_small(self) -> None:
        css = (ROOT / "docs/css/gallery.css").read_text()
        self.assertIn("repeat(auto-fill, minmax(min(100%, 10rem), 1fr))", css)

    def test_photo_directory_is_sorted_and_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            photos = Path(directory)
            for name in ["foto10.JPG", "foto2.png", "foto1.webp", "notes.txt"]:
                (photos / name).touch()

            html = _gallery_html(photos)
            tree = LexborHTMLParser(html)
            images = tree.css(".photo-gallery img")
            self.assertEqual(
                [image.attributes["src"].split("/")[-1] for image in images],
                ["foto1.webp", "foto2.png", "foto10.JPG"],
            )

    def test_site_build_has_lightbox_gallery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", directory],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            site = Path(directory)
            tree = LexborHTMLParser((site / "scuola-infanzia-rovereto/index.html").read_text())
            links = tree.css(".photo-gallery a.glightbox")
            self.assertEqual(len(links), 7)
            for number, link in enumerate(links, start=1):
                image = link.css_first("img")
                source = f"../immagini/scuola-infanzia-rovereto/2026-10-20_{number}.jpg"
                self.assertEqual(link.attributes["href"], source)
                self.assertEqual(link.attributes["data-gallery"], "scuola-infanzia-rovereto")
                self.assertEqual(image.attributes["src"], source)
                self.assertTrue(image.attributes["alt"])
                self.assertEqual(image.attributes["loading"], "lazy")
                self.assertTrue((site / "scuola-infanzia-rovereto" / source).is_file())

            self.assertIsNotNone(tree.css_first("script#init-glightbox"))
            self.assertIsNotNone(tree.css_first('link[href="../css/gallery.css"]'))
            self.assertTrue((site / "assets/javascripts/glightbox.min.js").is_file())
            self.assertTrue((site / "search/search_index.json").is_file())

    def test_serve_restarts_for_gallery_changes(self) -> None:
        script = (ROOT / "scripts/serve.sh").read_text()
        self.assertIn("watchmedo auto-restart -d . -d docs/immagini/scuola-infanzia-rovereto", script)
        self.assertIn("-p 'gallery.py;version.py;*.jpg;*.jpeg;*.png;*.webp'", script)
        self.assertIn("venv/bin/mkdocs serve --livereload -a 0.0.0.0:9000", script)
