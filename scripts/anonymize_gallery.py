"""Make face-only gallery copies from a reviewed JSON manifest of source photos."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def anonymize(source: Path, destination: Path, faces: list[list[int]]) -> None:
    with Image.open(source) as original:
        image = original.convert("RGB")

    for left, top, right, bottom, radius, feather in faces:
        blurred = image.filter(ImageFilter.GaussianBlur(radius))
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).ellipse((left, top, right, bottom), fill=255)
        image = Image.composite(blurred, image, mask.filter(ImageFilter.GaussianBlur(feather)))

    # Re-encoding also prevents source metadata (including GPS coordinates) from reaching the public gallery.
    image.save(destination, "JPEG", quality=92, optimize=True)


def process_manifest(source_dir: Path, gallery_dir: Path, manifest: Path) -> None:
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Manifest must be a list of photos")

    destinations: set[str] = set()
    for entry in entries:
        source_name = entry["source"]
        destination_name = entry["destination"]
        faces = entry["faces"]
        if (Path(source_name).name != source_name or Path(destination_name).name != destination_name
                or not destination_name.lower().endswith(".jpg")):
            raise ValueError("Use plain filenames and .jpg destinations")
        if destination_name in destinations or (gallery_dir / destination_name).exists():
            raise FileExistsError(f"Gallery photo already exists: {destination_name}")
        destinations.add(destination_name)
        if not (source_dir / source_name).is_file():
            raise FileNotFoundError(source_dir / source_name)
        for face in faces:
            if (len(face) != 6 or any(not isinstance(value, int) for value in face)
                    or face[0] >= face[2] or face[1] >= face[3] or face[4] <= 0 or face[5] < 0):
                raise ValueError(f"Invalid face region in {source_name}: {face}")

    # Check the entire batch before writing anything, so a typo cannot leave a partial gallery update.
    for entry in entries:
        anonymize(source_dir / entry["source"], gallery_dir / entry["destination"], entry["faces"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path, help="directory of untouched original JPEG photos")
    parser.add_argument("gallery_dir", type=Path, help="directory for public anonymized copies")
    parser.add_argument("manifest", type=Path, help="JSON list of source, destination, and face regions")
    arguments = parser.parse_args()
    process_manifest(arguments.source_dir, arguments.gallery_dir, arguments.manifest)


if __name__ == "__main__":
    main()
