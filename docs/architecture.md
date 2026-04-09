# AI Chat Application Architecture

## Overview

This document defines the clean architecture for the AI chat application, emphasizing **separation of concerns**, **testability**, **scalability**, and **maintainability**. The architecture follows Clean Architecture principles adapted for Python and specifically tailored for LLM/AI workloads.

---

## Core Principles

| Principle | Application |
|-----------|-------------|
| **Dependency Inversion** | Inner layers never depend on outer layers. Dependencies point inward. |
| **Single Responsibility** | Each module has one reason to change |
| **Explicit Dependencies** | Dependencies passed explicitly (no hidden global state) |
| **Interface Segregation** | Small, focused interfaces over large generic ones |
| **Bounded Contexts** | Clear boundaries between domain areas |

---

## Layer Structure

```
aichat/
├── src/
│   └── aichat/
│       ├── __init__.py
│       │
│       ├── config/                 # Configuration (innermost - no dependencies)
│       │   ├── __init__.py
│       │   ├── settings.py        # Pydantic BaseSettings for env management
│       │   ├── logging.py          # Logging configuration
│       │   └── prompts.py         # Prompt templates
│       │
│       ├── domain/                 # Domain Layer (CORE - pure business logic)
│       │   ├── __init__.py
│       │   ├── entities/           # Core business objects
│       │   │   ├── __init__.py
│       │   │   ├── message.py      # Chat message entity
│       │   │   ├── conversation.py # Conversation aggregate root
│       │   │   ├── user.py         # User entity
│       │   │   └── agent.py        # AI agent configuration
│       │   │
│       │   ├── value_objects/      # Immutable value types
│       │   │   ├── __init__.py
│       │   │   ├── message_id.py
│       │   │   ├── conversation_id.py
│       │   │   ├── token.py        # Token usage tracking
│       │   │   └── model_config.py # LLM config VO
│       │   │
│       │   ├── events/             # Domain events (optional - for event sourcing)
│       │   │   ├── __init__.py
│       │   │   ├── message_sent.py
│       │   │   ├── conversation_created.py
│       │   │   └── token_usage_recorded.py
│       │   │
│       │   ├── exceptions/         # Domain-specific exceptions
│       │   │   ├── __init__.py
│       │   │   ├── domain_error.py
│       │   │   └── exceptions.py
│       │   │
│       │   └── ports/              # INTERFACES (abstractions)
│       │       ├── __init__.py
│       │       ├── llm_provider.py  # LLM provider interface
│       │       ├── message_repository.py
│       │       ├── conversation_repository.py
│       │       ├── user_repository.py
│       │       ├── cache_port.py    # Caching abstraction
│       │       └── event_bus.py     # Event publishing abstraction
│       │
│       ├── application/            # Application Layer (use cases)
│       │   ├── __init__.py
│       │   │
│       │   ├── use_cases/          # Application services / Use cases
│       │   │   ├── __init__.py
│       │   │   ├── chat/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── send_message.py
│       │   │   │   ├── get_conversation.py
│       │   │   │   ├── create_conversation.py
│       │   │   │   └── stream_response.py
│       │   │   │
│       │   │   ├── conversation/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── list_conversations.py
│       │   │   │   ├── delete_conversation.py
│       │   │   │   └── search_conversations.py
│       │   │   │
│       │   │   └── agent/
│       │   │       ├── __init__.py
│       │   │       ├── create_agent.py
│       │   │       └── update_agent.py
│       │   │
│       │   ├── dto/                # Data Transfer Objects
│       │   │   ├── __init__.py
│       │   │   ├── message_dto.py
│       │   │   ├── conversation_dto.py
│       │   │   └── user_dto.py
│       │   │
│       │   ├── commands/           # CQRS Commands (if using CQRS)
│       │   │   ├── __init__.py
│       │   │   ├── send_message_command.py
│       │   │   └── create_conversation_command.py
│       │   │
│       │   ├── queries/            # CQRS Queries
│       │   │   ├── __init__.py
│       │   │   ├── get_conversation_query.py
│       │   │   └── list_conversations_query.py
│       │   │
│       │   └── interfaces/         # Service interfaces (implementations in infra)
│       │       ├── __init__.py
│       │       └── notification.py  # Notification service interface
│       │
│       ├── infrastructure/         # Infrastructure Layer (implementations)
│       │   ├── __init__.py
│       │   │
│       │   ├── llm/                # LLM Provider implementations
│       │   │   ├── __init__.py
│       │   │   ├── openai_provider.py
│       │   │   ├── anthropic_provider.py
│       │   │   ├── local_provider.py  # Ollama, LM Studio, etc.
│       │   │   └── factory.py         # Provider factory
│       │   │
│       │   ├── persistence/        # Repository implementations
│       │   │   ├── __init__.py
│       │   │   ├── database.py         # DB connection/session management
│       │   │   ├── repositories/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── message_repository_impl.py
│       │   │   │   ├── conversation_repository_impl.py
│       │   │   │   └── user_repository_impl.py
│       │   │   └── migrations/         # Alembic migrations
│       │   │       ├── __init__.py
│       │   │       └── versions/
│       │   │
│       │   ├── cache/              # Cache implementations
│       │   │   ├── __init__.py
│       │   │   ├── redis_cache.py
│       │   │   └── in_memory_cache.py
│       │   │
│       │   ├── messaging/          # Message queue implementations
│       │   │   ├── __init__.py
│       │   │   ├── redis_queue.py
│       │   │   └── rabbitmq_queue.py
│       │   │
│       │   ├── logging/            # Logging implementations
│       │   │   ├── __init__.py
│       │   │   └── structlog_config.py
│       │   │
│       │   └── events/             # Event bus implementations
│       │       ├── __init__.py
│       │       ├── in_memory_bus.py
│       │       └── redis_bus.py
│       │
│       ├── presentation/          # Presentation Layer (API, CLI, etc.)
│       │   ├── __init__.py
│       │   │
│       │   ├── api/                # REST/WebAPI
│       │   │   ├── __init__.py
│       │   │   ├── main.py             # FastAPI/Starlette app
│       │   │   ├── router.py           # Main router
│       │   │   ├── dependencies.py      # FastAPI dependencies
│       │   │   ├── middleware/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── auth.py
│       │   │   │   ├── rate_limit.py
│       │   │   │   └── tracing.py
│       │   │   ├── schemas/            # Pydantic request/response models
│       │   │   │   ├── __init__.py
│       │   │   │   ├── chat.py
│       │   │   │   ├── conversation.py
│       │   │   │   └── common.py
│       │   │   └── views/               # API endpoints
│       │   │       ├── __init__.py
│       │   │       ├── chat.py
│       │   │       ├── conversations.py
│       │   │       └── health.py
│       │   │
│       │   ├── ws/                 # WebSocket handlers
│       │   │   ├── __init__.py
│       │   │   ├── connection_manager.py
│       │   │   └── chat_websocket.py
│       │   │
│       │   ├── cli/                # CLI interface
│       │   │   ├── __init__.py
│       │   │   └── commands/
│       │   │       ├── __init__.py
│       │   │       ├── chat.py
│       │   │       └── config.py
│       │   │
│       │   └── workers/            # Background workers
│       │       ├── __init__.py
│       │       ├── processor.py
│       │       └── tasks/
│       │           ├── __init__.py
│       │           └── token_usage.py
│       │
│       └── shared/                 # Shared utilities (use with caution)
│           ├── __init__.py
│           ├── types.py            # Common type aliases
│           ├── datetime_utils.py
│           └── crypto_utils.py
│
├── tests/                          # Test structure mirrors src
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── fixtures/                   # Test data fixtures
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── test_messages.py
│   │   │   └── test_conversations.py
│   │   └── factories.py           # Factory for creating test objects
│   │
│   ├── unit/                       # Unit tests (fast, no I/O)
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_message.py
│   │   │   │   └── test_conversation.py
│   │   │   ├── value_objects/
│   │   │   │   └── test_token.py
│   │   │   └── test_aggregate.py   # Aggregate root tests
│   │   │
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── test_send_message.py
│   │   │       └── test_stream_response.py
│   │   │
│   │   └── infrastructure/
│   │       └── llm/
│   │           └── test_provider_factory.py
│   │
│   ├── integration/                # Integration tests (DB, external services)
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── test_chat_endpoint.py
│   │   │   └── conftest.py
│   │   │
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── test_message_repository.py
│   │
│   └── e2e/                        # End-to-end tests (full flow)
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_chat_flow.py
│       └── test_websocket_chat.py
│
├── scripts/                        # Utility scripts
│   ├── __init__.py
│   ├── generate_migrations.py
│   └── seed_data.py
│
├── docs/                           # Documentation
│   ├── architecture.md
│   ├── api.md
│   └── development.md
│
├── pyproject.toml
├── poetry.lock
├── .env.example
├── .env.test
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## Dependency Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│         (API, WebSocket, CLI - depends on Application)          │
└─────────────────────────────┬───────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│         (Use Cases, DTOs, Commands/Queries)                     │
│         - Orchestrates domain objects                           │
│         - No business logic (delegates to domain)               │
│         - Depends on Domain interfaces (ports)                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER                             │
│              (Entities, Value Objects, Ports)                    │
│         - Pure business logic, no external dependencies         │
│         - Defines interfaces (ports) for infrastructure        │
│         - No imports from outer layers                          │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ implements
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│     (Repository implementations, LLM providers, caching)        │
│         - Implements domain interfaces                          │
│         - Contains all external dependencies                    │
│         - Can have its own internal structure                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Decisions

### 1. Repository Pattern

**Why**: Decouples domain from persistence details. Enables testability through mocks.

```python
# Domain/ports/message_repository.py
from abc import ABC, abstractmethod
from typing import AsyncIterator
from aichat.domain.entities.message import Message

class MessageRepository(ABC):
    @abstractmethod
    async def save(self, message: Message) -> Message: ...
    
    @abstractmethod
    async def get_by_id(self, message_id: str) -> Message | None: ...
    
    @abstractmethod
    async def list_by_conversation(
        self, conversation_id: str, limit: int = 50
    ) -> list[Message]: ...
    
    @abstractmethod
    async def stream_by_conversation(
        self, conversation_id: str
    ) -> AsyncIterator[Message]: ...
```

### 2. LLM Provider Abstraction

**Why**: Allows swapping between OpenAI, Anthropic, local models, or mocking for tests.

```python
# Domain/ports/llm_provider.py
from abc import ABC, abstractmethod
from typing import AsyncIterator
from aichat.domain.value_objects.model_config import ModelConfig

class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self, 
        messages: list[dict[str, str]], 
        config: ModelConfig
    ) -> str: ...
    
    @abstractmethod
    async def stream(
        self, 
        messages: list[dict[str, str]], 
        config: ModelConfig
    ) -> AsyncIterator[str]: ...
    
    @abstractmethod
    async def get_token_count(self, text: str) -> int: ...
```

### 3. Service Layer Pattern

**Why**: Use cases that need orchestration of multiple repositories or domain services.

```python
# Application/use_cases/chat/send_message.py
from dataclasses import dataclass
from aichat.domain.entities.message import Message
from aichat.domain.entities.conversation import Conversation
from aichat.domain.ports import MessageRepository, LLMProvider
from aichat.application.dto import MessageDTO, SendMessageResult

@dataclass
class SendMessageUseCase:
    message_repo: MessageRepository
    llm_provider: LLMProvider
    
    async def execute(self, dto: MessageDTO) -> SendMessageResult:
        # Validate
        conversation = await self.message_repo.get_conversation(dto.conversation_id)
        if not conversation:
            raise ConversationNotFoundError(dto.conversation_id)
        
        # Create user message
        user_message = Message.create_user_message(dto.content, conversation.id)
        await self.message_repo.save(user_message)
        
        # Call LLM
        context = await self.message_repo.get_conversation_context(conversation.id)
        response = await self.llm_provider.complete(context, dto.model_config)
        
        # Create assistant message
        assistant_message = Message.create_assistant_message(response, conversation.id)
        await self.message_repo.save(assistant_message)
        
        return SendMessageResult(user_message, assistant_message)
```

### 4. Streaming with Async Generators

**Why**: Essential for LLM responses - users expect token-by-token streaming.

```python
# Application/use_cases/chat/stream_response.py
from typing import AsyncIterator
from aichat.domain.ports import MessageRepository, LLMProvider
from aichat.domain.entities.message import Message

class StreamResponseUseCase:
    async def execute(
        self, conversation_id: str, user_message: str
    ) -> AsyncIterator[str]:
        # Yield tokens as they arrive
        context = await self.message_repo.get_conversation_context(conversation_id)
        
        async for token in self.llm_provider.stream(context, config):
            yield token
```

### 5. Event-Driven Architecture (Optional)

**Why**: Useful for token usage tracking, analytics, notifications.

```python
# Domain/events/message_sent.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class MessageSentEvent:
    event_id: str
    occurred_at: datetime
    message_id: str
    conversation_id: str
    sender_type: str  # "user" | "assistant"
    token_count: int | None
    
# Infrastructure listens and handles
class TokenUsageHandler:
    async def handle(self, event: MessageSentEvent) -> None:
        await self.usage_tracker.record(event)
```

---

## Configuration Management

### Environment-Based Settings

```python
# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore unknown env vars
    )
    
    # Application
    app_name: str = "AIChat"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    
    # LLM Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_model: str = "gpt-4"
    default_temperature: float = 0.7
    
    # Database
    database_url: str = "sqlite:///./data/aichat.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Rate Limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 60  # seconds
    
    # Feature Flags
    enable_streaming: bool = True
    enable_analytics: bool = True

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### .env.example

```bash
# Application
APP_NAME="AIChat"
ENVIRONMENT="development"
DEBUG="true"

# LLM Providers
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
DEFAULT_MODEL="gpt-4"
DEFAULT_TEMPERATURE="0.7"

# Database
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/aichat"

# Redis
REDIS_URL="redis://localhost:6379"
REDIS_CACHE_TTL="3600"

# Rate Limiting
RATE_LIMIT_REQUESTS="60"
RATE_LIMIT_WINDOW="60"
```

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │    E2E      │  ← Few, slow, high confidence
        │   Tests     │     (Full flow, real DB)
       ┌┴─────────────┴┐
       │  Integration  │  ← Moderate, tests adapters
       │    Tests      │     (API endpoints, repos)
      ┌┴───────────────┴┐
      │     Unit        │  ← Many, fast, isolated
      │     Tests       │     (Domain logic, use cases)
      └─────────────────┘
```

### Test Organization

```python
# tests/unit/domain/entities/test_message.py
import pytest
from aichat.domain.entities.message import Message, MessageRole

class TestMessage:
    def test_create_user_message(self):
        message = Message.create_user_message(
            content="Hello, world!",
            conversation_id="conv-123"
        )
        
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.conversation_id == "conv-123"
        assert message.created_at is not None
    
    def test_empty_content_raises_error(self):
        with pytest.raises(ValueError):
            Message.create_user_message("", "conv-123")

# tests/integration/api/test_chat_endpoint.py
import pytest
from httpx import AsyncClient, ASGITransport
from aichat.presentation.api.main import app

class TestChatEndpoint:
    @pytest.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_send_message(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/chat/send",
            json={"conversation_id": "conv-123", "content": "Hello"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data
```

### Test Fixtures (Factory Pattern)

```python
# tests/factories.py
from factory import Factory, Faker, SubFactory
from aichat.domain.entities.message import Message, MessageRole
from aichat.domain.entities.conversation import Conversation

class ConversationFactory(Factory):
    class Meta:
        model = Conversation
    
    id = Faker("uuid4")
    title = Faker("sentence")
    created_at = Faker("date_time")

class MessageFactory(Factory):
    class Meta:
        model = Message
    
    id = Faker("uuid4")
    conversation = SubFactory(ConversationFactory)
    role = MessageRole.USER
    content = Faker("paragraph")
    created_at = Faker("date_time")
```

---

## Common Patterns for AI/LLM Applications

### 1. Message History Management

```python
# Domain/services/message_history.py
from typing import AsyncIterator
from aichat.domain.entities.message import Message

class MessageHistoryManager:
    """Manages conversation context within token limits."""
    
    def __init__(self, max_tokens: int = 128000):
        self.max_tokens = max_tokens
    
    async def build_context(
        self, 
        messages: AsyncIterator[Message],
        token_counter: callable
    ) -> list[dict[str, str]]:
        context = []
        total_tokens = 0
        
        async for message in messages:
            message_tokens = await token_counter(message.content)
            
            if total_tokens + message_tokens > self.max_tokens:
                break
                
            context.insert(0, message.to_dict())
            total_tokens += message_tokens
        
        return context
```

### 2. Token Usage Tracking

```python
# Domain/services/token_tracker.py
from dataclasses import dataclass
from datetime import datetime
from aichat.domain.value_objects.token import TokenUsage

@dataclass
class TokenUsageRecord:
    conversation_id: str
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: datetime
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def cost(self) -> float:
        # Model-specific pricing
        PRICING = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        }
        pricing = PRICING.get(self.model, {"input": 0, "output": 0})
        return (
            self.input_tokens / 1000 * pricing["input"] +
            self.output_tokens / 1000 * pricing["output"]
        )
```

### 3. Provider Fallback Strategy

```python
# Infrastructure/llm/factory.py
class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
        self._providers: dict[str, type[LLMProvider]] = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "local": LocalProvider,
        }
    
    def create(self, provider_name: str | None = None) -> LLMProvider:
        name = provider_name or self.config.default_model.split("-")[0]
        provider_class = self._providers.get(name, OpenAIProvider)
        return provider_class(self.config)
    
    async def create_with_fallback(
        self, 
        preferred: str, 
        fallback: str
    ) -> LLMProvider:
        """Try preferred, fall back on failure."""
        primary = self.create(preferred)
        
        # Wrap with fallback logic
        secondary = self.create(fallback)
        
        return FallbackProvider(primary, secondary)
```

### 4. Streaming Response Handler

```python
# Infrastructure/llm/streaming_handler.py
import asyncio
from typing import AsyncIterator

class StreamingResponseHandler:
    """Handles SSE/websocket streaming for LLM responses."""
    
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
    
    async def stream_to_queue(
        self, 
        token_stream: AsyncIterator[str],
        message_id: str
    ) -> None:
        """Stream tokens to a queue for websocket delivery."""
        async for token in token_stream:
            await self.queue.put({
                "type": "token",
                "message_id": message_id,
                "content": token
            })
        
        await self.queue.put({
            "type": "done",
            "message_id": message_id
        })
```

---

## Potential Issues to Avoid

| Issue | Problem | Solution |
|-------|---------|----------|
| **God Service** | One massive service class doing everything | Split by bounded context |
| **Premature Abstraction** | Abstracting everything "for flexibility" | Only abstract what varies or needs mocking |
| **Tight Coupling to LLM** | Direct OpenAI calls scattered everywhere | Always use Provider interface |
| **Sync I/O in Async Code** | Blocking calls in async handlers | Use async drivers (asyncpg, aioredis) |
| **Global State** | Singleton services, global config | Pass dependencies explicitly |
| **Anemic Domain** | Entities with no behavior, all logic in services | Rich domain models with invariants |
| **Ignore Token Limits** | Sending unbounded history to LLM | Implement context window management |
| **No Error Handling** | Bare `except Exception` swallowing errors | Specific exception types, proper propagation |
| **Leaking Infrastructure** | Domain importing SQLAlchemy, Redis | Domain has zero infrastructure imports |
| **Testing Without Mocks** | Integration tests hitting real APIs | Mock external services in unit tests |

---

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | `snake_case` | `message_repository.py` |
| Classes | `PascalCase` | `MessageRepository` |
| Functions | `snake_case` | `get_conversation` |
| Constants | `SCREAMING_SNAKE` | `MAX_TOKEN_LIMIT` |
| Private | `_leading_underscore` | `_internal_method` |
| DTOs | `*_dto.py` suffix | `message_dto.py` |
| Exceptions | `*_error.py` or `exceptions.py` | `domain_error.py` |
| Interfaces | `*_port.py` suffix | `llm_provider.py` |
| Implementations | `*_impl.py` or full name | `openai_provider.py` |
| Test files | `test_*.py` prefix | `test_message.py` |

---

## Dependency Injection Setup

```python
# presentation/api/dependencies.py
from functools import cached_property
from aichat.config.settings import get_settings
from aichat.infrastructure.llm.factory import LLMProviderFactory
from aichat.infrastructure.persistence.database import Database
from aichat.infrastructure.persistence.repositories import (
    MessageRepositoryImpl,
    ConversationRepositoryImpl,
)

class Container:
    """Simple dependency container for the application."""
    
    @cached_property
    def settings(self):
        return get_settings()
    
    @cached_property
    def database(self) -> Database:
        return Database(self.settings.database_url)
    
    @cached_property
    def llm_factory(self) -> LLMProviderFactory:
        return LLMProviderFactory(self.settings)
    
    @cached_property
    def message_repository(self) -> MessageRepository:
        return MessageRepositoryImpl(self.database)
    
    @cached_property
    def conversation_repository(self) -> ConversationRepository:
        return ConversationRepositoryImpl(self.database)
    
    # Use cases
    @cached_property
    def send_message(self) -> SendMessageUseCase:
        return SendMessageUseCase(
            message_repo=self.message_repository,
            llm_provider=self.llm_factory.create(),
        )

container = Container()

# FastAPI dependency injection
from fastapi import Depends

def get_send_message_use_case() -> SendMessageUseCase:
    return container.send_message
```

---

## Quick Start Checklist

- [ ] Set up project structure with `src/` and `tests/`
- [ ] Configure `pyproject.toml` with dependencies
- [ ] Implement domain entities first (no external deps)
- [ ] Define ports/interfaces in domain layer
- [ ] Implement infrastructure (repositories, LLM providers)
- [ ] Build use cases in application layer
- [ ] Create API endpoints in presentation layer
- [ ] Write unit tests for domain logic
- [ ] Write integration tests for repositories
- [ ] Configure CI/CD pipeline

---

## Recommended Stack

| Layer | Recommended | Alternatives |
|-------|-------------|---------------|
| API Framework | FastAPI | Starlette, Flask (with async) |
| Database | PostgreSQL + asyncpg | SQLite, MySQL |
| ORM | SQLAlchemy 2.0 (async) | Prisma, Tortoise |
| Cache | Redis | Memcached |
| Validation | Pydantic v2 | attrs + cattrs |
| Settings | pydantic-settings | dynaconf |
| Logging | structlog | loguru |
| Testing | pytest + pytest-asyncio | unittest |
| Migrations | Alembic | Flyway |

---

## Summary

This architecture provides:

1. **Clean separation** - Domain is pure Python, no framework imports
2. **Testability** - All external dependencies injectable, mockable
3. **Flexibility** - Easy to swap LLM providers, databases, caches
4. **Scalability** - Clear bounded contexts, async-first design
5. **Maintainability** - Explicit dependencies, small focused modules

The key insight for LLM applications: **always abstract the LLM provider** and **manage token usage carefully**. Everything else follows standard clean architecture principles.
