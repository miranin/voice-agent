"""
Scraper for https://kino.kz — movies, concerts, art events in Almaty.

Real HTML structure (verified 2026-03-12):
  The site covers movies AND live events (concerts, stand-up, art, entertainment).

  Event card: <a href="/ru/concert/event/XXXX"> or /ru/art/event/ /ru/entertainment/event/
  Title:      h4 inside the card
  Date+venue: p inside the card — "16 марта • Punch Stand-Up Club"
  Price:      span.rt-Badge (first one inside card) — "от 2 000 ₸"

  Movie card: <a href="/ru/cinema/...">
  Title:      h4 inside
  Date:       p inside

  We use href pattern as the stable selector since class names are CSS Modules hashes
  that may change on re-deploy.
"""

import re
import logging
from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..event_models import Event

logger = logging.getLogger(__name__)

BASE_URL = "https://kino.kz"
URL      = "https://kino.kz/ru"

# URL patterns for each event type
EVENT_PATTERNS = {
    "concert":      "/ru/concert/event/",
    "art":          "/ru/art/event/",
    "entertainment":"/ru/entertainment/event/",
    "movie":        "/ru/cinema/",
}


class KinoScraper(BaseScraper):
    source_name = "kino"
    base_url = BASE_URL

    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        events: List[Event] = []
        try:
            logger.info(f"[kino] Navigating to {URL}")
            await page.goto(URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(4_000)  # wait for React render

            # Find all event/movie card links using stable href patterns
            for category, path_prefix in EVENT_PATTERNS.items():
                selector = f'a[href^="{path_prefix}"]'
                cards = await page.query_selector_all(selector)
                logger.info(f"[kino] {category}: {len(cards)} cards")

                for card in cards:
                    try:
                        href  = await card.get_attribute("href") or ""
                        url   = f"{BASE_URL}{href}"

                        title_el  = await card.query_selector("h4")
                        detail_el = await card.query_selector("p")
                        price_el  = await card.query_selector("span.rt-Badge")

                        title = self._safe_text(
                            await title_el.inner_text() if title_el else None
                        )
                        if not title:
                            continue

                        detail = self._safe_text(
                            await detail_el.inner_text() if detail_el else None
                        )
                        price = self._safe_text(
                            await price_el.inner_text() if price_el else None
                        )

                        # detail format: "16 марта • Punch Stand-Up Club"
                        date, location = self._parse_detail(detail)

                        events.append(Event(
                            title=title,
                            date=date,
                            location=location,
                            price=price,
                            url=url,
                            source=self.source_name,
                            category=category,
                        ))

                    except Exception as e:
                        logger.warning(f"[kino] Card parse error ({category}): {e}")
                        continue

        except Exception as e:
            logger.error(f"[kino] Scraper failed: {e}")

        # Deduplicate by URL
        seen = set()
        unique = []
        for e in events:
            if e.url not in seen:
                seen.add(e.url)
                unique.append(e)

        logger.info(f"[kino] Returning {len(unique)} events")
        return unique

    def _parse_detail(self, detail: str | None):
        """
        Parse: "16 марта • Punch Stand-Up Club"
        Returns: (date, location)
        """
        if not detail:
            return None, None
        parts = detail.split("•", 1)
        date     = self._safe_text(parts[0]) if len(parts) >= 1 else None
        location = self._safe_text(parts[1]) if len(parts) == 2 else None
        return date, location
