"""
Abstract base class for all event scrapers.

To add a new website:
1. Create a new file in mcp_tools/sites/
2. Subclass BaseScraper
3. Implement the `scrape()` method
4. Register it in event_scraper.py
"""

from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import Page
from ..event_models import Event


class BaseScraper(ABC):
    """
    All scrapers inherit from this class.
    Each scraper is responsible for one website.
    """

    source_name: str = ""   # e.g. "sxodim", "ticketon", "kino"
    base_url: str = ""      # e.g. "https://sxodim.com"

    @abstractmethod
    async def scrape(self, page: Page, city: str = "Almaty") -> List[Event]:
        """
        Navigate to the site and return a list of Event objects.

        Args:
            page:  An active Playwright Page instance.
            city:  City name to filter events (default: "Almaty").

        Returns:
            List of Event objects. Return [] on any error — never raise.
        """
        ...

    def _safe_text(self, value: str | None) -> str | None:
        """Strip whitespace or return None if empty."""
        if not value:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None
