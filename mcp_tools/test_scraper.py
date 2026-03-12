"""
Quick test — run this to verify scrapers work before integrating with the agent.

    python -m mcp_tools.test_scraper
"""

import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

from mcp_tools.event_scraper import search_events


async def main():
    print("\n🔍 Searching events in Almaty...\n")
    events = await search_events(city="Almaty")

    if not events:
        print("⚠️  No events returned. Check selectors in sites/.")
        return

    print(f"✅ Found {len(events)} events:\n")
    for event in events:
        print(f"  [{event.source}] {event.title}")
        if event.date:
            print(f"           Date:     {event.date}")
        if event.time:
            print(f"           Time:     {event.time}")
        if event.location:
            print(f"           Location: {event.location}")
        if event.price:
            print(f"           Price:    {event.price}")
        if event.url:
            print(f"           URL:      {event.url}")
        print()

    # Also show raw JSON
    print("\n--- Raw JSON output ---")
    print(json.dumps(
        [e.model_dump(exclude_none=True) for e in events[:3]],
        ensure_ascii=False, indent=2
    ))


if __name__ == "__main__":
    asyncio.run(main())
