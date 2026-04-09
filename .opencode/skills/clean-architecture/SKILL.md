# Clean Architecture Skill

## Purpose
Enforce domain/application/infrastructure separation in the codebase.

## Layer Rules

```
presentation → application → domain ← infrastructure
```

| Layer | Rule | External Dependencies |
|-------|------|----------------------|
| `domain` | ZERO imports. Pure Python only | None |
| `application` | Imports domain only. No framework code | domain |
| `infrastructure` | Implements domain ports. All external deps here | domain, external libs |
| `presentation` | Depends on application. HTTP/WS handling | application, framework |

## File Structure
```
src/aichat/
├── domain/
│   ├── entities/       # Core business objects
│   ├── repositories/  # Port interfaces (abc)
│   ├── services/      # Domain services
│   └── exceptions.py  # Domain exceptions
├── application/
│   ├── use_cases/     # Business logic orchestration
│   ├── dto/           # Data transfer objects
│   └── ports/         # Port interfaces (impl)
├── infrastructure/
│   ├── repositories/   # Repository implementations
│   ├── external/      # External API clients
│   └── persistence/   # Database implementations
└── presentation/
    ├── api/           # FastAPI routes
    ├── cli/           # CLI commands
    └── websocket/     # WS handlers
```

## Layer Compliance Check

### Domain Layer
```python
# ✅ Valid - pure Python
class User:
    def __init__(self, id: UUID, email: str):
        self.id = id
        self.email = email

# ❌ Invalid - imports external
from pydantic import BaseModel  # NOT ALLOWED
```

### Application Layer
```python
# ✅ Valid - imports only domain
from aichat.domain.entities import User
from aichat.domain.repositories import UserRepository

# ❌ Invalid - imports infrastructure
from aichat.infrastructure.db import Session  # NOT ALLOWED
```

### Infrastructure Layer
```python
# ✅ Valid - implements domain ports
from aichat.domain.repositories import UserRepository
from sqlalchemy import select

class SQLAlchemyUserRepository(UserRepository):
    async def get_by_id(self, user_id: UUID) -> User | None:
        ...

# ❌ Invalid - domain cannot import this
# Domain should NOT import from infrastructure
```

## Dependency Injection
Pass dependencies via constructor or dependency injection framework:

```python
# application/use_cases/create_user.py
class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
    
    async def execute(self, dto: CreateUserDTO) -> User:
        ...

# infrastructure/di.py
def get_create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase(UserRepository())
```

## Violations
Report any layer violations. Never bypass the architecture.
