"""
Unified event search function.

This is the main entry point for the automation layer.
The LangChain tool and any other callers should use search_events().

Usage:
    import asyncio
    from mcp_tools.event_scraper import search_events

    events = asyncio.run(search_events(city="Almaty"))
"""

import asyncio
import logging
from typing import List

from .playwright_browser import BrowserManager
from .event_models import Event
from .sites import SxodimScraper, TicketonScraper, KinoScraper

logger = logging.getLogger(__name__)

# Register all scrapers here — add new ones to this list
SCRAPERS = [
    SxodimScraper(),
    TicketonScraper(),
    KinoScraper(),
]


async def search_events(city: str = "Almaty") -> List[Event]:
    """
    Run all scrapers concurrently and return merged results.

    Each scraper gets its own page. If one scraper fails, others continue.

    Args:
        city: City to search events in (default: "Almaty").

    Returns:
        List of Event objects from all sources, sorted by time.
    """
    async with BrowserManager() as browser:
        tasks = []
        pages = []

        for scraper in SCRAPERS:
            page = await browser.new_page()
            pages.append(page)
            tasks.append(scraper.scrape(page, city=city))

        # Run all scrapers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_events: List[Event] = []
    for scraper, result in zip(SCRAPERS, results):
        if isinstance(result, Exception):
            logger.error(f"[{scraper.source_name}] Scraper raised exception: {result}")
            continue
        all_events.extend(result)

    # Sort by time (events without time go to the end)
    all_events.sort(key=lambda e: e.time or "99:99")

    logger.info(f"[search_events] Total events found: {len(all_events)}")
    return all_events


def search_events_sync(city: str = "Almaty") -> List[Event]:
    """
    Synchronous wrapper around search_events().
    Use this when you cannot use async/await (e.g., in synchronous LangChain setups).
    """
    return asyncio.run(search_events(city=city))
