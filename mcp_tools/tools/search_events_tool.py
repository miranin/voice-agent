"""
LangChain-compatible tool that the AI agent calls to search for events.

The agent receives a plain-text summary of all found events.
It then decides how to respond to the user.

Usage in agent:
    from mcp_tools.tools import search_events_tool

    tools = [search_events_tool]
    agent = create_react_agent(llm, tools, prompt)
"""

import json
import logging
from langchain_core.tools import tool
from ..event_scraper import search_events_sync

logger = logging.getLogger(__name__)


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
    logger.info(f"[tool] search_events_tool called for city='{city}'")

    try:
        events = search_events_sync(city=city)

        if not events:
            return json.dumps({
                "status": "no_results",
                "message": f"No events found in {city} at the moment.",
                "events": [],
            }, ensure_ascii=False)

        events_data = [event.model_dump(exclude_none=True) for event in events]

        return json.dumps({
            "status": "success",
            "city": city,
            "total": len(events_data),
            "events": events_data,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"[tool] search_events_tool error: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to search events: {str(e)}",
            "events": [],
        }, ensure_ascii=False)
