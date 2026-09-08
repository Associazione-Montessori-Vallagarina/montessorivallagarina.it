# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The public website of *Associazione Montessori Vallagarina* (a parents/teachers association in
Rovereto, Trentino, Italy). It is a **MkDocs + Material** static site. There is no application code,
no test suite, and no linter — content is hand-written Markdown, almost entirely in **Italian**.
Match the existing Italian tone and terminology when editing or adding pages.

## Commands

All commands assume the local virtualenv in `venv/` (created from `requirements.txt`).

- **Serve locally with live reload:** `scripts/serve.sh` (runs `mkdocs serve -a 0.0.0.0:9000`)
- **Build the static site:** `venv/bin/mkdocs build` (output goes to `site/`, which is gitignored)
- **Deploy:** `scripts/publish.sh` (runs `mkdocs gh-deploy` — builds and force-pushes to the
  `gh-pages` branch of `origin`). This is the only deploy path; there is no CI. The live site is
  served from `gh-pages` at the custom domain in `docs/CNAME` (`montessorivallagarina.it`).
- **Set up the venv:** `python -m venv venv && venv/bin/pip install -r requirements.txt`

## Structure & conventions

- **`mkdocs.yml`** is the single source of site config. The `nav:` tree is manual — a new page does
  **not** appear in the site menu until it is added to `nav:`. New event pages go under the `Eventi:`
  section, newest first (the list is in reverse-chronological order).
- **`docs/`** is the content root (MkDocs `docs_dir`). Everything published lives here.
  - `docs/blog/` — dated event/news pages (`YYYY-MM.md`, or a descriptive slug for a specific
    event) plus their images. Image links inside `docs/blog/*.md` are **relative to `docs/blog/`**
    (e.g. `![](Litigare bene genitori.png)`), not to the site root.
  - `docs/immagini/` — shared images (logo, recurring photos like `aula.jpg`).
  - `docs/allegati/` — downloadable PDFs (membership forms, privacy docs).
  - `docs/CNAME` — custom-domain file; copied verbatim into the build. Do not remove it.
  - `docs/js/analytics.js` — a raw `<script>` snippet (Cloudflare Web Analytics) injected via
    `extra_javascript` in `mkdocs.yml`.
- Pages mix Markdown with inline HTML (`<span style=...>`, `<br>`, `<a target="_blank">`) — this is
  intentional and fine to continue.
- The association's IBAN (`IT33O0801120800000033314717`) and payment "causale" strings appear
  verbatim on several pages; keep them exactly consistent when updating one.

## Typical task: add a new event post

**An event post always goes in two places:** the blog archive and the home page. Keep the wording
of the two copies the same.

1. **Blog archive** — there is one page per month, `docs/blog/YYYY-MM.md` (older posts sometimes use
   a descriptive slug instead). Append the post as a new `## Titolo` section on that month's page,
   creating the file if the month has none yet. Put any images next to it in `docs/blog/`. This
   section is a **plain archive**: description and date only, **no reservation/registration link**.
2. If a new file was created, add it to `nav:` under `Eventi:` in `mkdocs.yml` (top of the list).
3. **Home page** — add the same post text to `docs/index.md` under `# Prossimi appuntamenti`. The
   reservation/registration link goes **only here**, as `<a href="..." target="_blank">`. **Remove
   past events** from this section at the same time (the blog archive keeps them; the home page only
   shows upcoming ones).
4. `scripts/serve.sh` to preview, then `scripts/publish.sh` to deploy.

Commit the Markdown/image source to `master`; never commit the `site/` build output or the
`gh-pages` branch by hand (`gh-deploy` manages it).
