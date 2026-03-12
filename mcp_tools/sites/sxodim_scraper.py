"""
Scraper for https://sxodim.com/almaty

Real HTML structure (verified 2026-03-12):
  Card:     div.impression-card
  Title+URL: a.impression-card-title  (the <a> IS both the link and the title text)
  Info:     div.impression-card-info  — "от 25 000 тенге, 17 марта в 20:00, Дворец Республики, 56"

The info string packs price, date, time, and location into one line — we parse it with regex.
"""

import re
import logging
from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..event_models import Event

logger = logging.getLogger(__name__)

URL = "https://sxodim.com/almaty"


class SxodimScraper(BaseScraper):
    source_name = "sxodim"
    base_url = "https://sxodim.com"

    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        events: List[Event] = []
        try:
            logger.info(f"[sxodim] Navigating to {URL}")
            await page.goto(URL, wait_until="domcontentloaded")
            await page.wait_for_selector(".impression-card", timeout=15_000)

            cards = await page.query_selector_all(".impression-card")
            logger.info(f"[sxodim] Found {len(cards)} cards")

            for card in cards:
                try:
                    title_el = await card.query_selector("a.impression-card-title")
                    info_el  = await card.query_selector(".impression-card-info")

                    if not title_el:
                        continue

                    title = self._safe_text(await title_el.inner_text())
                    if not title:
                        continue

                    href = await title_el.get_attribute("href") or ""
                    url  = href if href.startswith("http") else f"{self.base_url}{href}"

                    # Parse info string: "от 25 000 тенге, 17 марта в 20:00, Дворец Республики"
                    info = self._safe_text(await info_el.inner_text()) if info_el else None
                    date, time, price, location = self._parse_info(info)

                    events.append(Event(
                        title=title,
                        date=date,
                        time=time,
                        price=price,
                        location=location,
                        url=url,
                        source=self.source_name,
                    ))

                except Exception as e:
                    logger.warning(f"[sxodim] Card parse error: {e}")
                    continue

        except Exception as e:
            logger.error(f"[sxodim] Scraper failed: {e}")

        logger.info(f"[sxodim] Returning {len(events)} events")
        return events

    def _parse_info(self, info: str | None):
        """
        Parse: "от 25 000 тенге, 17 марта в 20:00, Дворец Республики, пр. Достык, 56"
        Returns: (date, time, price, location)
        """
        if not info:
            return None, None, None, None

        price = None
        date  = None
        time  = None
        location = None

        # Extract price: "от X тенге" or "от X ₸"
        price_match = re.search(r'(от[\s\d\u00a0]+(?:тенге|₸))', info, re.IGNORECASE)
        if price_match:
            price = price_match.group(1).strip()

        # Extract date + time: "17 марта в 20:00"
        dt_match = re.search(
            r'(\d{1,2}\s+[а-яёА-ЯЁ]+)\s+в\s+(\d{2}:\d{2})',
            info, re.IGNORECASE
        )
        if dt_match:
            date = dt_match.group(1).strip()
            time = dt_match.group(2).strip()

        # Location is everything after the time
        if dt_match:
            after_time = info[dt_match.end():]
            location = self._safe_text(after_time.lstrip(", "))

        return date, time, price, location
