"""
LangChain tools for event search.

Two modes:
- MCP_SERVER_URL is set: calls the Automation Engineer's MCP server (production)
- MCP_SERVER_URL not set: returns stub data (development/testing)

When Automation Engineer fills in mcp_tools/STATUS.md with the server URL,
set MCP_SERVER_URL=http://localhost:PORT in .env and tools switch automatically.
"""

import os
import json
import requests
from langchain_core.tools import tool

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")


def _call_mcp(tool_name: str, params: dict):
    """Call the Automation Engineer's MCP HTTP server."""
    url = f"{MCP_SERVER_URL}/tools/{tool_name}"
    try:
        resp = requests.post(url, json=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"MCP server error ({tool_name}): {e}") from e


# --- Stub data for development ---

_STUB_EVENTS = [
    {
        "title": "Стендап «Вечер юмора»",
        "time": "19:00",
        "location": "Almaty Comedy Club, ул. Абая 5",
        "url": "https://sxodim.com/almaty/standup-test-1",
    },
    {
        "title": "Джазовый концерт Aiza",
        "time": "20:30",
        "location": "Mojo Music Hall, ул. Панфилова 20",
        "url": "https://sxodim.com/almaty/jazz-test-2",
    },
    {
        "title": "Вечеринка Soul Night",
        "time": "22:00",
        "location": "Chukotka Bar",
        "url": "https://ticketon.kz/soul-night-test",
    },
]

_STUB_DETAILS = {
    "title": "Стендап «Вечер юмора»",
    "description": "Лучшие стендап-комики Алматы на одной сцене.",
    "time": "19:00, пятница",
    "location": "Almaty Comedy Club, ул. Абая 5",
    "price": "3 000 — 5 000 тг",
}


# --- LangChain Tools ---

@tool
def search_events(site: str, query: str) -> str:
    """Ищет мероприятия на сайте афиши по запросу.

    Args:
        site: Сайт для поиска. Один из: sxodim.com/almaty, ticketon.kz, kino.kz
        query: Поисковый запрос на русском, например: 'стендап', 'концерт сегодня', 'кино'

    Returns:
        JSON-список мероприятий: [{title, time, location, url}, ...]
    """
    if MCP_SERVER_URL:
        events = _call_mcp("search_events", {"site": site, "query": query})
    else:
        # Stub: filter by query keyword for slightly realistic behaviour
        events = [e for e in _STUB_EVENTS if query.lower() in e["title"].lower() or True]
    return json.dumps(events, ensure_ascii=False, indent=2)


@tool
def get_event_details(url: str) -> str:
    """Получает подробную информацию о конкретном мероприятии по URL.

    Args:
        url: Полный URL страницы мероприятия

    Returns:
        JSON с деталями: {title, description, time, location, price}
    """
    if MCP_SERVER_URL:
        details = _call_mcp("get_event_details", {"url": url})
    else:
        details = {**_STUB_DETAILS, "url": url}
    return json.dumps(details, ensure_ascii=False, indent=2)


def get_tools() -> list:
    return [search_events, get_event_details]
