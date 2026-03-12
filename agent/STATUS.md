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

Waiting for `mcp_tools/STATUS.md`. Tool interface expected:

| Tool | Input | Output |
|------|-------|--------|
| `search_events` | `{site, query}` | `[{title, time, location, url}]` |
| `get_event_details` | `{url}` | `{title, description, time, location, price}` |

When `MCP_SERVER_URL` is set in `.env`, agent automatically switches from stubs to real MCP server.
The MCP server must expose: `POST /tools/search_events` and `POST /tools/get_event_details`.

## Current Mode
- `MCP_SERVER_URL` not set → **stub mode** (returns test data, full pipeline works)
- `MCP_SERVER_URL` set → **production mode** (calls Automation Engineer's MCP server)

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
