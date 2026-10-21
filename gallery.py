import re
from html import escape
from pathlib import Path
from urllib.parse import quote

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page


GALLERY_MARKER = "<!-- galleria scuola infanzia -->"
GALLERY_DIRECTORY = "immagini/scuola-infanzia-rovereto"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _photo_order(path: Path) -> list[int | str]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", path.name)]


def _gallery_html(directory: Path) -> str:
    photos = sorted(
        (path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS),
        key=_photo_order,
    )
    if not photos:
        raise ValueError(f"Nessuna foto nella galleria: {directory}")

    images = []
    for number, photo in enumerate(photos, start=1):
        source = f"../{GALLERY_DIRECTORY}/{quote(photo.name)}"
        images.append(
            f'  <img class="on-glb" data-gallery="scuola-infanzia-rovereto" src="{escape(source, quote=True)}" '
            f'alt="Scuola dell\'infanzia Montessori, foto {number}" loading="lazy">'
        )
    return '<div class="photo-gallery">\n' + "\n".join(images) + "\n</div>"


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
    if page.file.src_uri != "scuola-infanzia-rovereto.md" or GALLERY_MARKER not in markdown:
        return markdown
    return markdown.replace(GALLERY_MARKER, _gallery_html(Path(config.docs_dir) / GALLERY_DIRECTORY))
