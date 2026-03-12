"""
Scraper for https://ticketon.kz — concerts, shows, sports events in Almaty.

HOW TO UPDATE SELECTORS:
1. Open https://ticketon.kz/city/almaty in Chrome
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
URL = "https://ticketon.kz/city/almaty"

SELECTORS = {
    "event_card": ".event-item, .tile, .events__item, article",
    "title":      ".event-item__title, .tile__title, h2, h3",
    "date":       ".event-item__date, .tile__date, time",
    "time":       ".event-item__time, .tile__time",
    "location":   ".event-item__place, .tile__place, .venue-name",
    "price":      ".event-item__price, .tile__price, .price",
    "link":       "a",
}
# -------------------------------------------------------------------


class TicketonScraper(BaseScraper):
    source_name = "ticketon"
    base_url = "https://ticketon.kz"

    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        events: List[Event] = []

        try:
            logger.info(f"[ticketon] Navigating to {URL}")
            await page.goto(URL, wait_until="domcontentloaded")

            # Ticketon may load content via JS — wait a moment
            await page.wait_for_timeout(2_000)
            await page.wait_for_selector(SELECTORS["event_card"], timeout=15_000)

            cards = await page.query_selector_all(SELECTORS["event_card"])
            logger.info(f"[ticketon] Found {len(cards)} event cards")

            for card in cards:
                try:
                    title_el    = await card.query_selector(SELECTORS["title"])
                    date_el     = await card.query_selector(SELECTORS["date"])
                    time_el     = await card.query_selector(SELECTORS["time"])
                    location_el = await card.query_selector(SELECTORS["location"])
                    price_el    = await card.query_selector(SELECTORS["price"])
                    link_el     = await card.query_selector(SELECTORS["link"])

                    title = self._safe_text(
                        await title_el.inner_text() if title_el else None
                    )
                    if not title:
                        continue

                    date_raw = self._safe_text(
                        await date_el.get_attribute("datetime")
                        or (await date_el.inner_text() if date_el else None)
                    )
                    time_raw  = self._safe_text(await time_el.inner_text()    if time_el    else None)
                    location  = self._safe_text(await location_el.inner_text() if location_el else None)
                    price     = self._safe_text(await price_el.inner_text()   if price_el   else None)

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
                    logger.warning(f"[ticketon] Failed to parse card: {e}")
                    continue

        except Exception as e:
            logger.error(f"[ticketon] Scraper failed: {e}")

        logger.info(f"[ticketon] Returning {len(events)} events")
        return events
