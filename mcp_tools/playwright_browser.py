"""
Async Playwright browser manager.

Usage:
    async with BrowserManager() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
"""

import asyncio
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, Page, Playwright


class BrowserManager:
    """
    Manages a single shared Playwright browser instance.
    Use as an async context manager to ensure proper cleanup.
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 30_000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def new_page(self) -> Page:
        if not self._browser:
            raise RuntimeError("BrowserManager not started. Use 'async with' or call start().")
        context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        page.set_default_timeout(self.timeout_ms)
        return page

    async def __aenter__(self) -> "BrowserManager":
        await self.start()
        return self

    async def __aexit__(self, *_) -> None:
        await self.stop()


@asynccontextmanager
async def get_page(headless: bool = True):
    """
    Convenience context manager that yields a ready Page.

    Usage:
        async with get_page() as page:
            await page.goto("https://sxodim.com")
    """
    async with BrowserManager(headless=headless) as browser:
        page = await browser.new_page()
        try:
            yield page
        finally:
            await page.context.close()
