"""
Scraper for https://sxodim.com — Almaty events (concerts, stand-up, exhibitions, etc.)

HOW TO UPDATE SELECTORS:
1. Open https://sxodim.com/almaty in Chrome
2. Right-click an event card → Inspect
3. Find the CSS selector for the element
4. Update the selector constants below
"""

import logging
from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..event_models import Event

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# CSS selectors — update here if the site changes layout
# -------------------------------------------------------------------
URL = "https://sxodim.com/almaty"

SELECTORS = {
    "event_card":  ".event-card, .events-list__item, article.event",
    "title":       ".event-card__title, h2, h3",
    "date":        ".event-card__date, .event__date, time",
    "time":        ".event-card__time, .event__time",
    "location":    ".event-card__place, .event__place, .venue",
    "price":       ".event-card__price, .event__price, .price",
    "link":        "a",
}
# -------------------------------------------------------------------


class SxodimScraper(BaseScraper):
    source_name = "sxodim"
    base_url = "https://sxodim.com"

    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        events: List[Event] = []

        try:
            logger.info(f"[sxodim] Navigating to {URL}")
            await page.goto(URL, wait_until="domcontentloaded")

            # Wait for event cards to load
            await page.wait_for_selector(SELECTORS["event_card"], timeout=15_000)

            cards = await page.query_selector_all(SELECTORS["event_card"])
            logger.info(f"[sxodim] Found {len(cards)} event cards")

            for card in cards:
                try:
                    title_el   = await card.query_selector(SELECTORS["title"])
                    date_el    = await card.query_selector(SELECTORS["date"])
                    time_el    = await card.query_selector(SELECTORS["time"])
                    location_el = await card.query_selector(SELECTORS["location"])
                    price_el   = await card.query_selector(SELECTORS["price"])
                    link_el    = await card.query_selector(SELECTORS["link"])

                    title = self._safe_text(
                        await title_el.inner_text() if title_el else None
                    )
                    if not title:
                        continue  # skip cards without a title

                    date_raw = self._safe_text(
                        await date_el.get_attribute("datetime")
                        or (await date_el.inner_text() if date_el else None)
                    )
                    time_raw   = self._safe_text(await time_el.inner_text()   if time_el   else None)
                    location   = self._safe_text(await location_el.inner_text() if location_el else None)
                    price      = self._safe_text(await price_el.inner_text()  if price_el  else None)

                    href = await link_el.get_attribute("href") if link_el else None
                    url  = f"{self.base_url}{href}" if href and href.startswith("/") else href

                    events.append(Event(
                        title=title,
                        date=date_raw,
                        time=time_raw,
                        location=location,
                        price=price,
                        url=url,
                        source=self.source_name,
                    ))

                except Exception as e:
                    logger.warning(f"[sxodim] Failed to parse card: {e}")
                    continue

        except Exception as e:
            logger.error(f"[sxodim] Scraper failed: {e}")

        logger.info(f"[sxodim] Returning {len(events)} events")
        return events
