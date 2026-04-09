# AI Chat

A modern, scalable AI chat application with multi-LLM support, streaming responses, and enterprise-grade features.

## Vision

A seamless conversational experience with multiple LLM providers, robust user management, and collaboration features for individuals and teams.

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React/TypeScript (planned)
- **Database**: PostgreSQL with SQLAlchemy (planned)
- **Cache**: Redis (planned)
- **LLM Providers**: OpenAI, Anthropic, Ollama (planned)

## Architecture

Clean architecture with strict layer separation:

```
presentation → application → domain ← infrastructure
```

| Layer | Purpose |
|-------|---------|
| `domain` | Pure business logic, zero external dependencies |
| `application` | Use cases, domain imports only |
| `infrastructure` | External implementations (DB, APIs) |
| `presentation` | API handlers, WebSocket |

## Development

### Setup

```bash
# Clone the repo
git clone git@github.com:adityadroid/synthesis.git
cd synthesis

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies (when implemented)
pip install -r requirements.txt
```

### Code Standards

- Type hints on all functions
- Async/await throughout
- No bare `except Exception`
- Layer compliance enforced

See [AGENTS.md](AGENTS.md) for full guidelines.

## Roadmap

| Phase | Version | Focus | Tasks |
|-------|---------|-------|-------|
| MVP | v0.1.0 | Foundation (auth, core chat) | [001-009](tasks/) |
| Phase 1 | v1.0.0 | Essential features (multi-model, history) | [010-037](tasks/) |
| Phase 2 | v1.1.0 | Enhanced experience (search, export, customization) | [038-065](tasks/) |
| Phase 3 | v2.0.0 | Advanced features (teams, analytics) | [066-084](tasks/) |
| Infrastructure | All | Cross-cutting concerns | [085-101](tasks/) |

See [docs/product-roadmap.md](docs/product-roadmap.md) for full roadmap.

## Task Management

All executable tasks are documented in `/tasks/` with:
- Serial number (001-101)
- Phase tag
- Requirements and acceptance criteria
- Dependencies

### Task Status Tracking

Progress is tracked in [tasks/TRACKING.md](tasks/TRACKING.md):

| Phase | Total | Backend | Frontend | Shared | Completed |
|-------|-------|---------|----------|--------|-----------|
| MVP | 9 | 2 | 1 | 6 | 0/9 |
| Phase 1 | 31 | 3 | 16 | 12 | 0/31 |
| Phase 2 | 26 | 3 | 14 | 9 | 0/26 |
| Phase 3 | 19 | 6 | 0 | 13 | 0/19 |
| Infrastructure | 17 | 17 | 0 | 0 | 0/17 |
| **Total** | **102** | **31** | **31** | **40** | **0/102** |

**To update status:** Edit `tasks/TRACKING.md` - change `pending` to `in_progress` when starting, then `completed` when done.

### Skills

Agent skills for consistent execution:

- `.opencode/skills/task-execution/` - Individual task execution
- `.opencode/skills/phase-execution/` - Phase-level execution
- `.opencode/skills/clean-architecture/` - Architecture enforcement
- `.opencode/skills/fastapi-crud/` - CRUD patterns

## Contributing

1. Check the [roadmap](docs/product-roadmap.md) for features
2. Pick an incomplete task from [/tasks/](tasks/)
3. Follow [AGENTS.md](AGENTS.md) guidelines
4. Ensure layer compliance
5. Write tests
6. Submit PR

## License

MIT
