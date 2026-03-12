# AI Engineer Status

## Last Updated
2026-03-12

## Current Status
[x] Agent implemented and ready for integration

## Agent Interface (for Backend Engineer)

```python
from agent.agent import run_agent

result = run_agent(user_text="Куда сходить сегодня вечером?")
# Returns:
# {
#   "response_text": "Сегодня есть стендап в 19:00 в Almaty Comedy Club...",
#   "sources": [{"title": "Стендап «Вечер юмора»", "url": "https://sxodim.com/..."}]
# }
```

## Installation

```bash
pip install -r agent/requirements.txt
```

## Environment Variables

```env
OPENAI_API_KEY=your_key_here          # required
OPENAI_MODEL=gpt-4o-mini              # optional, default: gpt-4o-mini
MCP_SERVER_URL=http://localhost:8001  # optional, set when mcp_tools server is ready
```

## MCP Tools I'm Using

Integrated `mcp_tools.tools.search_events_tool` (Automation Engineer's module).

| Tool | Input | Output |
|------|-------|--------|
| `search_events_tool` | `city: str = "Almaty"` | `{status, city, total, events: [{title, date, time, location, price, url, source, category}]}` |

## Current Mode
- `mcp_tools` importable (playwright installed) → **production mode** (real scrapers: sxodim, ticketon, kino)
- `mcp_tools` not importable → **stub mode** (test data, pipeline still works)

## Files

```
agent/
├── agent.py      # run_agent() — public API for Backend Engineer
├── tools.py      # LangChain tools with MCP/stub switching
├── prompts.py    # LangChain system prompt (Russian, voice-friendly)
├── requirements.txt
└── STATUS.md
```

## Blockers
- Need Automation Engineer to fill `mcp_tools/STATUS.md` with:
  - HTTP server URL and port
  - Exact endpoint paths for tools

## Done
- [x] `run_agent(user_text) -> {response_text, sources}` implemented
- [x] LangChain agent with `gpt-4o-mini` and tool calling
- [x] `search_events` and `get_event_details` tools defined
- [x] Stub mode for development (no MCP dependency)
- [x] Production mode via `MCP_SERVER_URL` env var
- [x] System prompt in Russian, voice-friendly output
