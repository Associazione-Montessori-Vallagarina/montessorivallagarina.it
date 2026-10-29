import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

from mkdocs.config.defaults import MkDocsConfig
from selectolax.lexbor import LexborHTMLParser

from events import Event, _event_page, _events, _month_index, _upcoming, on_config


ROOT = Path(__file__).resolve().parents[1]
EVENT = Event("blog/2026-11-11_genitori-senza-mantello.md", "Genitori senza mantello",
              date(2026, 11, 11), ("2026-11-07.jpg",), "https://forms.gle/3P2bMHKGmZdxthgS8")


class TestEvents(unittest.TestCase):
    def test_new_month_is_added_to_menu_from_front_matter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            blog = Path(directory) / "blog"
            blog.mkdir()
            (blog / "2027-01-12_test.md").write_text(
                "---\ntitle: Un nuovo evento\nevent_date: 2027-01-12\nflyer: [locandina.jpg]\n---\n"
                "\nUna descrizione con **dettagli**.\n"
            )
            (blog / "2027-02-04_test.md").write_text(
                "---\ntitle: Un altro evento\nevent_date: 2027-02-04\nflyer: [locandina.jpg]\n---\n"
            )
            config = MagicMock(spec=MkDocsConfig)
            config.docs_dir = directory
            config.nav = [{"Eventi": [{"Ottobre 2026": "blog/2026-10.md"}]}]

            events = _events(config)
            self.assertEqual([event.date for event in events], [date(2027, 2, 4), date(2027, 1, 12)])
            self.assertEqual(events[1].description.strip(), "Una descrizione con **dettagli**.")
            self.assertIs(on_config(config), config)
            self.assertEqual(config.nav[0]["Eventi"], [
                {"Febbraio 2027": "blog/2027-02.md"},
                {"Gennaio 2027": "blog/2027-01.md"},
                {"Ottobre 2026": "blog/2026-10.md"},
            ])

    def test_home_shows_event_until_its_date(self) -> None:
        event = replace(EVENT, description="Una descrizione con **dettagli**.")
        for day in (date(2026, 11, 10), EVENT.date):
            with self.subTest(day=day):
                upcoming = _upcoming([event], day)
                self.assertIn("blog/2026-11-11_genitori-senza-mantello.md", upcoming)
                self.assertIn("blog/2026-11-07.jpg", upcoming)
                self.assertIn(EVENT.registration_url, upcoming)
                self.assertIn("Una descrizione con **dettagli**.", upcoming)
                self.assertIn('data-share-url="blog/2026-11-11_genitori-senza-mantello/"', upcoming)

        self.assertEqual(_upcoming([EVENT], date(2026, 11, 12)), "")

    def test_share_button_is_compact_and_text_only(self) -> None:
        css = (ROOT / "docs/css/events.css").read_text()
        self.assertIn("font-size: 0.75rem", css)
        self.assertIn(">Copia il link</span>", _event_page(EVENT, "", EVENT.date))
        self.assertNotIn("🔗", _event_page(EVENT, "", EVENT.date))

    def test_event_page_keeps_archive_but_expires_registration(self) -> None:
        current = _event_page(EVENT, "Una descrizione.", EVENT.date)
        expired = _event_page(EVENT, "Una descrizione.", date(2026, 11, 12))
        self.assertIn(EVENT.registration_url, current)
        self.assertNotIn(EVENT.registration_url, expired)
        self.assertIn("Una descrizione.", expired)
        self.assertIn("2026-11-07.jpg", expired)
        self.assertIn('class="event-share"', expired)

    def test_additional_flyer_appears_with_page_relative_path(self) -> None:
        event = replace(EVENT, flyers=("2026-11-07.jpg", "2026-11-07_tea_e_chicco.jpg"))
        self.assertIn("![Genitori senza mantello](2026-11-07_tea_e_chicco.jpg)",
                      _event_page(event, "", EVENT.date))
        self.assertIn("![Genitori senza mantello](blog/2026-11-07_tea_e_chicco.jpg)",
                      _upcoming([event], date(2026, 11, 1)))

    def test_month_shows_full_event_even_after_date(self) -> None:
        event = replace(EVENT, description="Una descrizione con **dettagli**.")
        index = _month_index([event], EVENT.date)
        self.assertIn("# Novembre 2026", index)
        self.assertIn("[Genitori senza mantello](2026-11-11_genitori-senza-mantello.md)", index)
        self.assertIn('data-share-url="../2026-11-11_genitori-senza-mantello/"', index)
        self.assertIn("11 novembre 2026", index)
        self.assertIn("![Genitori senza mantello](2026-11-07.jpg)", index)
        self.assertIn("Una descrizione con **dettagli**.", index)
        self.assertIn(EVENT.registration_url, index)
        self.assertNotIn(EVENT.registration_url, _month_index([event], date(2026, 11, 12)))

    def test_strict_build_has_event_page_month_and_share_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", directory],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            site = Path(directory)
            home = LexborHTMLParser((site / "index.html").read_text())
            month = LexborHTMLParser((site / "blog/2026-11/index.html").read_text())
            event = LexborHTMLParser((site / "blog/2026-11-11_genitori-senza-mantello/index.html").read_text())

            nav = home.css(".md-nav__item a")
            self.assertTrue(any(link.text(strip=True) == "Novembre 2026" and
                                link.attributes["href"] == "blog/2026-11/" for link in nav))
            self.assertEqual(month.css_first(".md-content h2 a").attributes["href"],
                             "../2026-11-11_genitori-senza-mantello/")
            self.assertEqual(month.css_first(".event-share").attributes["data-share-url"],
                             "../2026-11-11_genitori-senza-mantello/")
            self.assertEqual(month.css_first(".md-content img").attributes["src"], "../2026-11-07.jpg")
            if date.today() <= EVENT.date:
                self.assertIsNotNone(month.css_first('a[href="https://forms.gle/3P2bMHKGmZdxthgS8"]'))
            self.assertEqual(event.css_first(".md-content h1").text(strip=True), "Genitori senza mantello")
            self.assertIsNotNone(event.css_first(".event-share"))
            self.assertEqual(event.css_first(".md-content img").attributes["src"], "../2026-11-07.jpg")
            self.assertIsNotNone(home.css_first('script[src="js/events.js"]'))
            self.assertIsNotNone(home.css_first('link[href="css/events.css"]'))
            if date.today() <= EVENT.date:
                self.assertEqual(home.css_first(".event-share").attributes["data-share-url"],
                                 "blog/2026-11-11_genitori-senza-mantello/")
