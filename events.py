from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page
from mkdocs.utils import meta


HOME_MARKER = "<!-- prossimi eventi -->"
MONTHS = (
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
)


@dataclass(frozen=True)
class Event:
    path: str
    title: str
    date: date
    flyer: str
    registration_url: str | None
    description: str = ""

    @property
    def month(self) -> str:
        return f"{self.date:%Y-%m}"

    @property
    def month_title(self) -> str:
        return f"{MONTHS[self.date.month - 1]} {self.date.year}"

    @property
    def date_label(self) -> str:
        return f"{self.date.day} {MONTHS[self.date.month - 1].lower()} {self.date.year}"


def _events(config: MkDocsConfig) -> list[Event]:
    events = []
    for path in sorted((Path(config.docs_dir) / "blog").glob("*.md")):
        description, metadata = meta.get_data(path.read_text(encoding="utf-8"))
        if "event_date" not in metadata:
            continue
        event_date = metadata["event_date"]
        if not isinstance(event_date, date):
            raise ValueError(f"event_date deve essere una data YYYY-MM-DD: {path}")
        for field in ("title", "flyer"):
            if not isinstance(metadata.get(field), str) or not metadata[field]:
                raise ValueError(f"{field} mancante: {path}")
        registration_url = metadata.get("registration_url")
        if registration_url is not None and not isinstance(registration_url, str):
            raise ValueError(f"registration_url non valido: {path}")
        events.append(Event(f"blog/{path.name}", metadata["title"], event_date,
                            metadata["flyer"], registration_url, description))
    return sorted(events, key=lambda event: (event.date, event.path), reverse=True)


def _share_button(url: str = "") -> str:
    target = f' data-share-url="{escape(url, quote=True)}"' if url else ""
    return (f'<button type="button" class="event-share"{target} '
            'aria-label="Copia il link all’evento">'
            '<span class="event-share-label" aria-live="polite">Copia il link</span></button>')


def _month_index(events: list[Event], today: date) -> str:
    lines = [f"# {events[0].month_title}"]
    for event in events:
        name = Path(event.path).name
        lines.extend(("", _render_event(event, event.description, today,
                                        f"## [{event.title}]({name})", f"../{Path(name).stem}/")))
    return "\n".join(lines) + "\n"


def _upcoming(events: list[Event], today: date) -> str:
    lines = []
    for event in events:
        if event.date < today:
            continue
        lines.extend((f"## [{event.title}]({event.path})", event.date_label, "",
                      _share_button(f"blog/{Path(event.path).stem}/"), "",
                      f"![{event.title}](blog/{event.flyer})", ""))
        if event.description.strip():
            lines.extend((event.description.strip(), ""))
        if event.registration_url:
            lines.extend((f'<a href="{escape(event.registration_url, quote=True)}" target="_blank">'
                          "Clicca qui per prenotarsi all'attività</a>", ""))
    return "\n".join(lines).rstrip()


def _render_event(event: Event, description: str, today: date, heading: str, share_url: str) -> str:
    lines = [heading, "", _share_button(share_url), "", event.date_label, "",
             f"![{event.title}]({event.flyer})"]
    if description.strip():
        lines.extend(("", description.strip()))
    if event.registration_url and event.date >= today:
        lines.extend(("", f'<a href="{escape(event.registration_url, quote=True)}" target="_blank">'
                      "Clicca qui per prenotarsi all'attività</a>"))
    return "\n".join(lines) + "\n"


def _event_page(event: Event, description: str, today: date) -> str:
    return _render_event(event, description, today, f"# {event.title}", "")


def on_config(config: MkDocsConfig) -> MkDocsConfig:
    months = {}
    for event in _events(config):
        months[event.month] = event.month_title
    for item in config.nav:
        if isinstance(item, dict) and "Eventi" in item:
            # Generated months lead the legacy archive without changing its existing links.
            item["Eventi"] = [{title: f"blog/{month}.md"} for month, title in sorted(months.items(), reverse=True)] \
                + item["Eventi"]
            break
    return config


def on_files(files: Files, config: MkDocsConfig) -> Files:
    months: dict[str, list[Event]] = {}
    for event in _events(config):
        months.setdefault(event.month, []).append(event)
    for month, month_events in months.items():
        if any(file.src_uri == f"blog/{month}.md" for file in files):
            raise ValueError(f"La pagina mensile blog/{month}.md esiste già")
        files.append(File.generated(config, f"blog/{month}.md", content=_month_index(month_events, date.today())))
    return files


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
    events = _events(config)
    if page.file.src_uri == "index.md":
        return markdown.replace(HOME_MARKER, _upcoming(events, date.today()))
    for event in events:
        if page.file.src_uri == event.path:
            return _event_page(event, markdown, date.today())
    return markdown
