"""
Scraper for https://ticketon.kz

NOTE: ticketon.kz uses a queue-it virtual waiting room (anti-bot system).
Access from non-Kazakhstan IPs is blocked in the queue before the page loads.
This means the scraper may return 0 results when running outside Kazakhstan.

If you have a Kazakhstan IP (or a VPN), the site loads normally.
The scraper is kept here as a placeholder and will work when network access allows.

HOW TO UPDATE SELECTORS when queue-it is bypassed:
1. Open https://ticketon.kz/city/almaty in Chrome (from KZ network)
2. Inspect event card elements
3. Update SELECTORS below
"""

import logging
from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..event_models import Event

logger = logging.getLogger(__name__)

URL = "https://ticketon.kz/city/almaty"

SELECTORS = {
    "event_card": ".event-item, .product-card, .tile, article",
    "title":      ".event-item__title, .product-card__title, h2, h3",
    "date":       ".event-item__date, .product-card__date, time",
    "location":   ".event-item__place, .product-card__place",
    "price":      ".event-item__price, .product-card__price, .price",
    "link":       "a",
}

# Selector that appears on the actual ticketon page (not the queue page)
QUEUE_INDICATOR = "queue-it"
CONTENT_INDICATOR = ".event-item, .product-card"


class TicketonScraper(BaseScraper):
    source_name = "ticketon"
    base_url = "https://ticketon.kz"

    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        events: List[Event] = []
        try:
            logger.info(f"[ticketon] Navigating to {URL}")
            await page.goto(URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3_000)

            # Detect if we're stuck in the queue-it waiting room
            current_url = page.url
            page_html   = await page.content()
            if QUEUE_INDICATOR in page_html or "queue" in current_url.lower():
                logger.warning(
                    "[ticketon] Blocked by queue-it waiting room. "
                    "This usually means access from a non-Kazakhstan IP. "
                    "Skipping ticketon — returning 0 events."
                )
                return []

            await page.wait_for_selector(SELECTORS["event_card"], timeout=10_000)
            cards = await page.query_selector_all(SELECTORS["event_card"])
            logger.info(f"[ticketon] Found {len(cards)} cards")

            for card in cards:
                try:
                    title_el    = await card.query_selector(SELECTORS["title"])
                    date_el     = await card.query_selector(SELECTORS["date"])
                    location_el = await card.query_selector(SELECTORS["location"])
                    price_el    = await card.query_selector(SELECTORS["price"])
                    link_el     = await card.query_selector(SELECTORS["link"])

                    title = self._safe_text(
                        await title_el.inner_text() if title_el else None
                    )
                    if not title:
                        continue

                    date     = self._safe_text(await date_el.inner_text()     if date_el     else None)
                    location = self._safe_text(await location_el.inner_text() if location_el else None)
                    price    = self._safe_text(await price_el.inner_text()    if price_el    else None)
                    href     = await link_el.get_attribute("href")             if link_el     else None
                    url      = f"{self.base_url}{href}" if href and href.startswith("/") else href

                    events.append(Event(
                        title=title,
                        date=date,
                        location=location,
                        price=price,
                        url=url,
                        source=self.source_name,
                    ))

                except Exception as e:
                    logger.warning(f"[ticketon] Card parse error: {e}")
                    continue

        except Exception as e:
            logger.error(f"[ticketon] Scraper failed: {e}")

        logger.info(f"[ticketon] Returning {len(events)} events")
        return events
