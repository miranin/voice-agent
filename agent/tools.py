"""
LangChain tools for the AI agent.

Uses search_events_tool from mcp_tools (Automation Engineer's module).
Falls back to stub tool if mcp_tools/Playwright is not available (e.g. CI, dev without browser).
"""

import json
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

try:
    from mcp_tools.tools import search_events_tool
    _MCP_AVAILABLE = True
    logger.info("[tools] Using real mcp_tools.search_events_tool")
except ImportError:
    _MCP_AVAILABLE = False
    logger.warning("[tools] mcp_tools not available, using stub")


if not _MCP_AVAILABLE:
    @tool
    def search_events_tool(city: str = "Almaty") -> str:
        """
        Search for events (concerts, stand-up, movies, exhibitions) in the given city.

        Use this tool when the user asks about what to do, where to go,
        what events are happening, or anything related to entertainment.

        Args:
            city: The city to search events in. Default is "Almaty".

        Returns:
            A JSON string with a list of events including title, date, time,
            location, price, and source website.
        """
        logger.info(f"[stub] search_events_tool called for city='{city}'")
        return json.dumps({
            "status": "success",
            "city": city,
            "total": 2,
            "events": [
                {
                    "title": "Стендап «Вечер юмора»",
                    "date": "2026-03-12",
                    "time": "19:00",
                    "location": "Almaty Comedy Club, ул. Абая 5",
                    "price": "3 000 тг",
                    "url": "https://sxodim.com/almaty/standup-test",
                    "source": "sxodim",
                    "category": "standup",
                },
                {
                    "title": "Джазовый концерт Aiza",
                    "date": "2026-03-12",
                    "time": "20:30",
                    "location": "Mojo Music Hall, ул. Панфилова 20",
                    "price": "5 000 тг",
                    "url": "https://ticketon.kz/jazz-test",
                    "source": "ticketon",
                    "category": "concert",
                },
            ],
        }, ensure_ascii=False, indent=2)


def get_tools() -> list:
    return [search_events_tool]
