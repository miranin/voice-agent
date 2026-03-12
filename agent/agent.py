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
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.tools import get_tools
from agent.prompts import SYSTEM_PROMPT

load_dotenv()


def _build_executor() -> AgentExecutor:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    tools = get_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=5)


def _extract_sources(intermediate_steps: list) -> list:
    """Pull event sources from search_events_tool results."""
    sources = []
    for action, observation in intermediate_steps:
        if action.tool == "search_events_tool":
            try:
                data = json.loads(observation)
                for event in data.get("events", []):
                    if event.get("url") and event.get("title"):
                        sources.append({"title": event["title"], "url": event["url"]})
            except (json.JSONDecodeError, TypeError):
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
    executor = _build_executor()
    result = executor.invoke(
        {"input": user_text},
        return_only_outputs=False,
    )

    response_text = result.get("output", "")
    sources = _extract_sources(result.get("intermediate_steps", []))

    return {
        "response_text": response_text,
        "sources": sources,
    }
