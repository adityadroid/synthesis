# Justfile - Standard commands for Synthesis
# https://github.com/casey/just
#
# Usage: just <recipe>
# Examples:
#   just          # Show available commands
#   just fe-dev   # Start frontend dev server
#   just be-run   # Run backend server

# ===========================================
# DEFAULT - Show help
# ===========================================
default:
    @just --list

# ===========================================
# FRONTEND COMMANDS
# ===========================================

# Install frontend dependencies
fe-install:
    cd frontend && npm install

# Start frontend dev server (port 5173)
fe-dev:
    cd frontend && npm run dev

# Start frontend dev server on specific port
fe-dev-port PORT:
    cd frontend && npm run dev -- --port {{PORT}}

# Build frontend for production
fe-build:
    cd frontend && npm run build

# Preview production build
fe-preview:
    cd frontend && npm run preview

# Lint frontend
fe-lint:
    cd frontend && npm run lint

# ===========================================
# BACKEND COMMANDS
# ===========================================

# Install backend dependencies
be-install:
    cd backend && pip install -r requirements.txt

# Run backend server (port 8000)
be-run:
    cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# Run backend server on specific port
be-run-port PORT:
    cd backend && source venv/bin/activate && uvicorn src.main:app --reload --port {{PORT}}

# Run backend with custom host
be-run-host HOST PORT:
    cd backend && source venv/bin/activate && uvicorn src.main:app --reload --host {{HOST}} --port {{PORT}}

# Run backend database migrations
be-migrate:
    cd backend && source venv/bin/activate && alembic upgrade head

# Create backend database migration
be-migration NAME:
    cd backend && source venv/bin/activate && alembic revision --autogenerate -m "{{NAME}}"

# ===========================================
# TEST COMMANDS
# ===========================================

# Run frontend tests
fe-test:
    cd frontend && npm run test

# Run frontend tests with coverage
fe-test-cov:
    cd frontend && npm run test -- --coverage

# Run backend tests
be-test:
    cd backend && source venv/bin/activate && pytest

# Run backend tests with coverage
be-test-cov:
    cd backend && source venv/bin/activate && pytest --cov

# ===========================================
# HELPER COMMANDS
# ===========================================

# Start all services (frontend + backend)
all:
    @echo "Starting backend..."
    @just be-run &
    @echo "Starting frontend..."
    @just fe-dev &
    @echo ""
    @echo "Services started:"
    @echo "  Frontend: http://localhost:5173"
    @echo "  Backend:  http://localhost:8000"

# Kill all running servers
kill:
    pkill -f "vite" || true
    pkill -f "uvicorn" || true

# Show running processes
ps:
    @echo "Running processes:"
    @ps aux | grep -E "(vite|uvicorn)" | grep -v grep || echo "No processes found"