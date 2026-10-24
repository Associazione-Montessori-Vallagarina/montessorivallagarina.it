# Project instructions

This repository is the public website of *Associazione Montessori Vallagarina*, a parents/teachers
association in Rovereto, Trentino. It is a MkDocs + Material site with mostly Italian Markdown content.
Match the existing Italian tone and terminology when editing pages.

## Commands

Use the local `venv/` created from `requirements.txt`:

- Set up: `python -m venv venv && venv/bin/pip install -r requirements.txt`.
- Preview with live reload: `scripts/serve.sh` (serves on port 9000).
- Test: `venv/bin/python -m unittest discover -s tests`.
- Build: `venv/bin/mkdocs build --strict` (`site/` is ignored by Git).
- Deploy only when explicitly requested: `scripts/publish.sh` runs `mkdocs gh-deploy`, which
  force-pushes `origin/gh-pages`. There is no CI. The live site uses the domain in `docs/CNAME`.

## Site structure and conventions

- `mkdocs.yml` is the site configuration. Its `nav:` is manual: add new event pages under `Eventi:`,
  newest first, or they will not appear in the menu.
- `docs/` is the published content root. `docs/blog/` holds dated event pages and their images;
  image links in those pages are relative to `docs/blog/`. `docs/immagini/` holds shared images;
  `docs/allegati/` holds downloadable PDFs. Keep `docs/CNAME` intact.
- `docs/js/analytics.js` is a raw analytics snippet loaded through `extra_javascript`.
- Pages intentionally mix Markdown and inline HTML (`<span>`, `<br>`, `<a target="_blank">`).
- Keep the association's IBAN and payment "causale" text consistent across pages; do not improvise
  either value when editing a payment page.
- `gallery.py` generates the Rovereto school photo gallery; `tests/` contains the site and gallery tests.
- Commit Markdown and image sources to `master`, never `site/` or the `gh-pages` branch by hand.

## Adding an event post

For events from November 2026 onward, create one `docs/blog/YYYY-MM-DD_slug.md` per event with YAML
front matter (`title`, `event_date: YYYY-MM-DD`, `flyer`, and optional `registration_url`). Place the
flyer alongside the page; its path is relative to `docs/blog/`. Add any extra description below the
front matter. The `events.py` hook renders the event heading, date, flyer, description and compact
share button on both the event page and the monthly archive, as well as the monthly menu entry and
upcoming home-page entry. Do not add these by hand. Events remain on the home page through their
event date, and leave it on the next build after that date; the registration link also disappears
from the event page and monthly archive then. Rebuild/deploy manually for date
changes to appear on the published site. Existing monthly posts and home-page entries are still
maintained manually until migrated.

For older monthly posts, use the existing workflow:

An event goes in both the blog archive and the home page, with matching wording. A flyer usually
already has all the details: use a short title, date, and image; **do not copy text from the flyer**.
When a separate description is supplied, place it below the flyer. Put shared text for multiple
events once above those events. Upcoming events need their registration link in both copies:
`<a href="..." target="_blank">Clicca qui per prenotarsi all'attività</a>`.

1. Append the post to `docs/blog/YYYY-MM.md`, or create the file if needed. Keep its flyer alongside
   it, named `YYYY-MM-DD.jpg` (add a `_slug` suffix if multiple flyers share a date). Older posts
   sometimes use a descriptive slug instead of a monthly page. Retain past posts in the archive,
   but remove their registration links.
2. Add a newly created blog page to `mkdocs.yml` under `Eventi:`, newest first.
3. Add the same upcoming post under `# Prossimi appuntamenti` in `docs/index.md`, prefixing the
   image path with `blog/`. Remove past events from the home page at the same time.
4. Preview with `scripts/serve.sh`. Deploy with `scripts/publish.sh` only when requested.

## Working on the Rovereto school photo gallery

The public photos are in `docs/immagini/scuola-infanzia-rovereto/`. Incoming **private originals** live
in its `new/` directory, which Git ignores and MkDocs excludes from publication. Never commit `new/` or
remove the site exclusion. Do not publish the site until the built output has been checked for originals.

1. Compare incoming files with existing gallery photos by SHA-256. Remove from `new/` only confirmed
   byte-for-byte duplicates; inspect possible visually similar duplicates before deciding. Keep all
   non-duplicate originals in `new/`, unedited. Do not treat an anonymized public copy as a duplicate
   of its original.
2. Inspect every unique original **at full resolution**. Locate every visible face, including partial,
   distant and background faces; children photographed only from behind need no blur. Blur faces only,
   not whole heads or hair. Crop or zoom to verify the exact bounds, especially near image edges.
3. Copy `scripts/rovereto-2026-10-22.json` as a model for a new manifest. Each entry has an original
   `source` filename, a public `destination` name (`YYYY-MM-DD_N.jpg`, continuing after existing files
   for that date), and `faces`: `[left, top, right, bottom, blur_radius, edge_feather]` for each face.
   Coordinates are source-image pixels; regions can extend past image edges. Use `faces: []` when no
   face is visible. The previous manifest documents the actual masks used for the 2026-10-22 batch.
4. Run `venv/bin/python scripts/anonymize_gallery.py docs/immagini/scuola-infanzia-rovereto/new
   docs/immagini/scuola-infanzia-rovereto /tmp/opencode/rovereto-manifest.json`. Install dependencies
   from `requirements.txt` if necessary. The script does not overwrite existing public files. For
   corrections, edit the manifest and regenerate into a separate temporary folder; after visual
   inspection, replace only the intended public files. Never process an already blurred copy.
5. Review **each output at full size**, next to its original: all visible facial features hidden, hair
   and surroundings intact, no missed faces, no unnecessary blur. Verify every JPEG opens. Run
   `venv/bin/python -m unittest discover -s tests` and a strict MkDocs build; verify the build contains
   no `immagini/scuola-infanzia-rovereto/new/` files. Add only reviewed public images and any relevant
   script/instruction changes to Git; never use `git add` on the whole photo directory.
