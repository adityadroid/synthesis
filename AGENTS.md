# AI Chat - Agent Guidelines

## Core Principles

1. **Plan First** - Think before you code. Outline approach before execution.
2. **Document Decisions** - Always explain WHAT you did and WHY in code comments and PRs.
3. **Be Concise** - Save tokens. No fluff, no repetition, no pleasantries.
4. **Create Skills** - Extract repeatable patterns into skills/tools.
5. **Respect Architecture** - Follow `/docs/architecture.md` strictly.

---

## Workflow

### Before Writing Code

```
1. Understand → Parse requirements, ask clarifying questions
2. Plan → Outline approach, identify files affected
3. Delegate → Split work, use specialists if beneficial
4. Execute → Implement with minimal iterations
5. Verify → Check for errors, run tests
```

### File Changes

| Action | Document |
|--------|----------|
| New file | WHY it exists, what it does |
| Modified file | WHAT changed, WHY the change |
| Deleted file | WHY it was removed |
| Architecture change | Update `/docs/architecture.md` |

---

## Code Standards

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `SCREAMING_SNAKE_CASE`
- Private: `_leading_underscore`

### Type Hints
- All functions require type hints
- Use `None` instead of `Optional[]`
- Prefer `|` over `Union[]`

### Docstrings
- Use for public APIs only
- Concise: "Send message to LLM." not paragraphs
- Example:
```python
def send_message(user_id: str, content: str) -> Message:
    """Send a message and return the created message."""
```

---

## Layer Compliance

```
presentation → application → domain ← infrastructure
```

| Layer | Rule |
|-------|------|
| `domain` | ZERO external imports. Pure Python only. |
| `application` | Imports domain only. No framework code. |
| `infrastructure` | Implements domain ports. All external deps here. |
| `presentation` | Depends on application. HTTP/WebSocket handling. |

**Violations**: Always report. Never bypass.

---

## Skills

### When to Create

Create a skill when:
- Pattern repeated 3+ times
- Complex setup with multiple steps
- Configuration-dependent setup

### Skill Structure

```
skills/
├── skill_name/
│   ├── description.md
│   ├── instructions.md
│   └── templates/
```

### Existing Skills

- `fastapi-crud` - Standard CRUD patterns for FastAPI routes
- `clean-architecture` - Domain/application/infrastructure separation

---

## Documentation

### What to Document

| Type | Where | When |
|------|-------|------|
| Architecture decisions | `/docs/architecture.md` | On change |
| API changes | `/docs/api.md` | On endpoint add/modify |
| Setup/Config | `/docs/development.md` | On env change |
| Inline comments | Code | On complex logic |

### Commit Messages

Format: `type: brief description`

```
feat: add conversation rename
fix: resolve token overflow in long contexts
docs: update API endpoint specs
refactor: extract LLM provider abstraction
test: add unit tests for message truncation
```

---

## Error Handling

1. **Specific exceptions** - Never catch bare `Exception`
2. **Log context** - Include request_id, user_id where available
3. **Graceful degradation** - Return sensible defaults on failure
4. **User-friendly messages** - Don't expose raw errors

---

## Testing

| Level | Scope | When |
|-------|-------|------|
| Unit | Domain logic | Always |
| Integration | Repositories, APIs | On DB/network changes |
| E2E | Full flows | On significant features |

---

## Token Conservation

### Do
- Use file references, not full contents
- Summarize code, don't paste
- Direct answers, no preamble
- One-liners when appropriate

### Don't
- "Great question!" or similar filler
- Repeat what you did (show the result)
- Explain obvious code
- Verbose debugging output

---

## Quick Reference

### Key Files

| Path | Purpose |
|------|---------|
| `docs/architecture.md` | Architecture rules |
| `docs/product-roadmap.md` | Feature priorities |
| `src/aichat/domain/` | Pure business logic |
| `src/aichat/application/` | Use cases |
| `src/aichat/infrastructure/` | External implementations |
| `src/aichat/presentation/` | API/CLI/WS handlers |

### Important Patterns

- **Dependency Injection** - Pass dependencies, don't create them
- **Repository Pattern** - Interfaces in domain, impl in infrastructure
- **Async First** - Use async/await throughout
- **Ports & Adapters** - Domain defines contracts

---

## Anti-Patterns

❌ Direct OpenAI/Anthropic calls in use cases  
❌ `SELECT *` queries  
❌ Global state (singletons, globals)  
❌ Sync I/O in async handlers  
❌ Bare `except Exception`  
❌ Magic strings/numbers  
❌ Domain importing SQLAlchemy/Redis/Pydantic  
❌ Skipping tests "for now"  
