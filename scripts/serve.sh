#!/bin/sh
# Incremental builds do not rerun the gallery hook for newly added image files.
# Explicit live reload is needed because the installed Click version leaves the CLI default disabled.
exec venv/bin/watchmedo auto-restart -d . -d docs/immagini/scuola-infanzia-rovereto \
  -p 'gallery.py;*.jpg;*.jpeg;*.png;*.webp' -- venv/bin/mkdocs serve --livereload -a 0.0.0.0:9000
