import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.anonymize_gallery import process_manifest


class TestAnonymizeGallery(unittest.TestCase):
    def test_face_only_and_metadata_removed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            originals = root / "new"
            gallery = root / "gallery"
            originals.mkdir()
            gallery.mkdir()
            image = Image.new("RGB", (100, 100), (25, 130, 200))
            for x in range(35, 65):
                for y in range(35, 65):
                    image.putpixel((x, y), (x * 3, y * 3, 0))
            metadata = Image.Exif()
            metadata[315] = "private photographer"
            image.save(originals / "original.jpg", exif=metadata)
            before = (originals / "original.jpg").read_bytes()
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([{
                "source": "original.jpg", "destination": "2026-10-22_1.jpg",
                "faces": [[32, 32, 68, 68, 15, 3]],
            }]))

            process_manifest(originals, gallery, manifest)

            with Image.open(originals / "original.jpg") as source, Image.open(gallery / "2026-10-22_1.jpg") as result:
                self.assertEqual(source.getexif()[315], "private photographer")
                face_before = source.getpixel((50, 50))
                face_after = result.getpixel((50, 50))
                self.assertGreater(sum(abs(old - new) for old, new in zip(face_before, face_after)), 50)
                self.assertEqual(source.getpixel((0, 0)), result.getpixel((0, 0)))
                self.assertFalse(result.getexif())
            self.assertEqual((originals / "original.jpg").read_bytes(), before)

    def test_existing_destination_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source").mkdir()
            (root / "gallery").mkdir()
            (root / "gallery/photo.jpg").write_bytes(b"existing")
            manifest = root / "manifest.json"
            manifest.write_text('[{"source": "original.jpg", "destination": "photo.jpg", "faces": []}]')

            with self.assertRaises(FileExistsError):
                process_manifest(root / "source", root / "gallery", manifest)
            self.assertEqual((root / "gallery/photo.jpg").read_bytes(), b"existing")

    def test_invalid_batch_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source").mkdir()
            (root / "gallery").mkdir()
            Image.new("RGB", (10, 10)).save(root / "source/original.jpg")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([
                {"source": "original.jpg", "destination": "first.jpg", "faces": []},
                {"source": "missing.jpg", "destination": "second.jpg", "faces": []},
            ]))

            with self.assertRaises(FileNotFoundError):
                process_manifest(root / "source", root / "gallery", manifest)
            self.assertEqual(list((root / "gallery").iterdir()), [])
