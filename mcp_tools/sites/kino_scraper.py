"""
Scraper for https://kino.kz — cinema showtimes in Almaty.

kino.kz has a different structure: movies with multiple showtimes per day.
We flatten each showtime into a separate Event so the agent gets clean entries.

HOW TO UPDATE SELECTORS:
1. Open https://kino.kz/almaty in Chrome
2. Right-click a movie block → Inspect
3. Find CSS selectors and update below
"""

import logging
from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..event_models import Event

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
URL = "https://kino.kz/almaty"

SELECTORS = {
    "movie_card":  ".movie, .movie-card, .film-item, article.film",
    "title":       ".movie__title, .film-title, h2, h3",
    "cinema":      ".cinema-name, .movie__cinema, .session__cinema",
    "showtime":    ".showtime, .session-time, .time-slot",
    "link":        "a",
}
# -------------------------------------------------------------------


class KinoScraper(BaseScraper):
    source_name = "kino"
    base_url = "https://kino.kz"

    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        events: List[Event] = []

        try:
            logger.info(f"[kino] Navigating to {URL}")
            await page.goto(URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2_000)
            await page.wait_for_selector(SELECTORS["movie_card"], timeout=15_000)

            movies = await page.query_selector_all(SELECTORS["movie_card"])
            logger.info(f"[kino] Found {len(movies)} movie blocks")

            for movie in movies:
                try:
                    title_el  = await movie.query_selector(SELECTORS["title"])
                    link_el   = await movie.query_selector(SELECTORS["link"])
                    cinema_el = await movie.query_selector(SELECTORS["cinema"])

                    title = self._safe_text(
                        await title_el.inner_text() if title_el else None
                    )
                    if not title:
                        continue

                    href = await link_el.get_attribute("href") if link_el else None
                    url  = f"{self.base_url}{href}" if href and href.startswith("/") else href
                    cinema = self._safe_text(
                        await cinema_el.inner_text() if cinema_el else None
                    )

                    # Each movie may have multiple showtimes — create one Event per time
                    showtime_els = await movie.query_selector_all(SELECTORS["showtime"])

                    if showtime_els:
                        for st_el in showtime_els:
                            time_raw = self._safe_text(await st_el.inner_text())
                            events.append(Event(
                                title=title,
                                time=time_raw,
                                location=cinema,
                                url=url,
                                source=self.source_name,
                                category="movie",
                            ))
                    else:
                        # No showtimes found — still include the movie
                        events.append(Event(
                            title=title,
                            location=cinema,
                            url=url,
                            source=self.source_name,
                            category="movie",
                        ))

                except Exception as e:
                    logger.warning(f"[kino] Failed to parse movie: {e}")
                    continue

        except Exception as e:
            logger.error(f"[kino] Scraper failed: {e}")

        logger.info(f"[kino] Returning {len(events)} events")
        return events
