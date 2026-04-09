# AI Chat Application Architecture

## Philosophy

> "If you can't explain the architecture to a junior dev in 5 minutes, it's too complex."

This project uses a **pragmatic 3-layer architecture**. Keep it flat, keep it simple, keep it working.

---

## Backend: 3 Layers

```
src/
├── main.py           # FastAPI app entry
├── routes/           # HTTP handlers (thin - just request/response)
├── services/         # Business logic (where the work happens)
├── models/           # Pydantic schemas (request/response)
├── db.py             # Database connection
└── config.py         # Settings
```

### Rules

| Layer | Responsibility |
|-------|----------------|
| **routes/** | Parse request → call service → return response. Zero business logic. |
| **services/** | All business logic. Database calls. LLM calls. |
| **models/** | Pydantic schemas for request validation and response serialization. |

**No "ports" or "domain" layers unless you actually need to swap implementations.**

---

## Frontend: Modern React

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/              # API client + shared types
│   │   ├── client.ts
│   │   └── types.ts
│   ├── components/       # UI components
│   │   ├── Chat/
│   │   └── ui/
│   ├── hooks/            # Custom hooks (streaming, auth, etc)
│   └── pages/
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### Stack

- **Framework**: React 19 + Vite
- **State**: TanStack Query (server state), React Context (client state)
- **Validation**: Zod
- **UI**: shadcn-ui + Radix + Framer Motion
- **Types**: Shared with backend via OpenAPI or manual sync

---

## Database

PostgreSQL + asyncpg + SQLAlchemy 2.0 (async).

```
db.py: handles connection, session, base model
models/  # SQLAlchemy ORM models
```

---

## Real-Time

- **Streaming**: Server-Sent Events (SSE) for LLM token streaming
- **WebSocket**: Only for presence/collaboration features

---

## Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    model_config = {"env_file": ".env"}
```

---

## What We Don't Do

| Skip | Reason |
|------|--------|
| Clean Architecture layers | Overhead for a 5-15k LOC project |
| Repository pattern | SQLAlchemy is sufficient abstraction |
| Event sourcing | Just save to DB |
| CQRS | Single DB, simple reads/writes |
| DTOs separate from models | Just use Pydantic |

---

## Testing

| Level | Target | Tool |
|-------|--------|------|
| Unit | Business logic in services | pytest |
| API | All endpoints | httpx |
| E2E | Critical flows only | Playwright |
| Frontend Unit | Components | Vitest + RTL |

---

## Quick Reference

### Creating a new API endpoint

1. Add route in `routes/chat.py`
2. Add service function in `services/chat.py`
3. Add Pydantic models in `models/chat.py`
4. Test it

### Adding a frontend component

1. Create in `components/Chat/` or `components/ui/`
2. Use TanStack Query for data
3. Use `useChatStream` hook for streaming

---

## Summary

- **Backend**: routes → services → db (3 layers)
- **Frontend**: React + Vite + TanStack Query
- **DB**: PostgreSQL + asyncpg
- **Real-time**: SSE for streaming
- **Keep it flat, keep it working**
