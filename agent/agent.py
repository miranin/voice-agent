"""
AI Engineer module — LangChain agent for Voice AI Event Assistant.

Public interface for Backend Engineer:
    from agent.agent import run_agent

    result = run_agent("Куда сходить сегодня вечером?")
    # {
    #   "response_text": "Сегодня есть стендап в 19:00...",
    #   "sources": [{"title": "...", "url": "..."}]
    # }
"""

import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from agent.tools import get_tools
from agent.prompts import SYSTEM_PROMPT

load_dotenv()


def _build_agent():
    tools = get_tools()
    return create_agent(
        model=ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )


def _extract_sources(messages: list) -> list:
    """Pull event sources from tool result messages."""
    sources = []
    for msg in messages:
        # Tool messages contain the JSON response from search_events_tool
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                data = json.loads(msg.content)
                if isinstance(data, dict) and "events" in data:
                    for event in data["events"]:
                        if event.get("url") and event.get("title"):
                            sources.append({"title": event["title"], "url": event["url"]})
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
    return sources


def run_agent(user_text: str) -> dict:
    """
    Process a user voice query and return a response with sources.

    Args:
        user_text: Transcribed user speech, e.g. "Куда сходить сегодня вечером?"

    Returns:
        {
            "response_text": str,   # voice-friendly response in Russian
            "sources": [{"title": str, "url": str}, ...]
        }
    """
    agent = _build_agent()
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_text}]
    })

    messages = result.get("messages", [])

    # Last AI message is the final response
    response_text = ""
    for msg in reversed(messages):
        role = getattr(msg, "type", "") or getattr(msg, "role", "")
        if role in ("ai", "assistant") and getattr(msg, "content", ""):
            response_text = msg.content
            break

    sources = _extract_sources(messages)

    return {
        "response_text": response_text,
        "sources": sources,
    }
