# fastapi-agent

Bootcamp assignment project: FastAPI chat agent with session-based conversation history, streaming responses (SSE), and a web search tool.

## Monorepo Note

This backend now lives in `apps/backend`. Run the commands below from that directory.

## What This Project Does

- Manages chat **sessions** (`ChatSession`) and **messages** (`ChatMessage`) in a SQLite database.
- Exposes a chat endpoint that streams assistant output using **Server-Sent Events (SSE)**.
- Supports attaching a user-uploaded **text file** to a chat message (via a separate upload endpoint).
- Provides an agent tool: `search_web` (DuckDuckGo search via `ddgs`).

## Tech Stack

- Python + FastAPI
- SQLModel + Alembic (SQLite)
- `openai-agents` SDK with `LitellmModel` (configured for OpenRouter)
- `ddgs` for web search

## Setup

### 1) Install dependencies

This project uses `uv`.

```bash
uv sync
```

### 2) Environment variables

Create a `.env` file (do not commit it) and set at least:

- `OPENROUTER_API_KEY` (required)

Optional:

- `OPENROUTER_BASE_URL` (default: `https://openrouter.ai/api/v1`)
- `DATABASE_URL` (default: `sqlite:///./dev.db`)
- `UPLOAD_DIR` (default in code: `temp`)

### 3) Database migration

```bash
uv run alembic upgrade head
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

Open API docs (Scalar):

- `GET /scalar`

## API Usage

### Sessions (for sidebar/pagination)

- `GET /chat-sessions?limit=5&offset=0`

### Upload a file (text only)

Upload first, then pass the returned `file_path` to `/chat`.

```bash
curl -F "file=@./notes.txt" http://localhost:8000/uploads/
```

Response example:

```json
{
  "file_path": "/abs/path/to/temp/<uuid>-notes.txt",
  "filename": "notes.txt",
  "content_type": "text/plain"
}
```

### Chat (SSE streaming)

New chat: send `session_id: 0`.  
Continue a chat: send the existing `session_id`.

Without file:

```bash
curl -N \
  -H "Content-Type: application/json" \
  -d '{"session_id":0,"message":"Halo, cariin info FastAPI streaming SSE."}' \
  http://localhost:8000/chat/
```

With file attachment (use `file_path` from `/uploads`):

```bash
curl -N \
  -H "Content-Type: application/json" \
  -d '{"session_id":0,"message":"Ringkas isi file ini ya.","file_path":"<file_path_from_uploads>"}' \
  http://localhost:8000/chat/
```

SSE events include:

- `text_delta`: incremental assistant text chunks
- `tool_call`: emitted when the agent calls `search_web`
- `done`: end of stream

## Tools

- `search_web(query: str)` — runs DuckDuckGo search via `ddgs`

## Notes / Limitations

- File attachments are currently limited to **UTF-8 text files** (txt/md/json).
- This is a learning project. Error handling and persistence for tool outputs can be expanded.

## AI Assistance Disclosure

I used an AI coding assistant as a *mentor/pair-programmer* to accelerate learning and reduce time spent on syntax and debugging.

What AI was used for:

- Explaining architecture decisions (session/message persistence, tool calling, streaming).
- Reviewing repo structure and pointing out bugs/edge cases.
- Helping debug runtime errors (FastAPI dependency injection, async streaming, Alembic issues).
- Producing small code templates/snippets to give an example (SSE event generator patterns, `ddgs` tool wrapper, upload endpoint shape).
- Improving docs and API contracts (what endpoints exist and how to call them).

The final code was iteratively integrated and tested locally while ensuring I understand the reasoning behind each change.
