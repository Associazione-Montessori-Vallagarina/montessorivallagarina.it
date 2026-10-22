# Working on the Rovereto school photo gallery

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
