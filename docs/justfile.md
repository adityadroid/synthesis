# Justfile Reference

Standard commands for running, building, and testing Synthesis.

## Installation

```bash
# Install just (macOS)
brew install just

# Or via cargo
cargo install just
```

## Usage

Run `just` with no arguments to see all available commands, or `just --list`.

## Frontend Commands

| Command | Description |
|---------|-------------|
| `just fe-install` | Install npm dependencies |
| `just fe-dev` | Start Vite dev server (port 5173) |
| `just fe-dev-port 5174` | Start on specific port |
| `just fe-build` | Build for production |
| `just fe-preview` | Preview production build |
| `just fe-lint` | Run ESLint |
| `just fe-test` | Run frontend tests |

## Backend Commands

| Command | Description |
|---------|-------------|
| `just be-install` | Install Python dependencies |
| `just be-run` | Start backend server (port 8000) |
| `just be-run-port 8001` | Start on specific port |
| `just be-run-host 0.0.0.0 8000` | Start with custom host/port |
| `just be-migrate` | Run database migrations |
| `just be-migration add-users` | Create new migration |
| `just be-test` | Run backend tests |

## Combined Commands

| Command | Description |
|---------|-------------|
| `just all` | Start both frontend + backend |
| `just kill` | Kill all running servers |
| `just ps` | Show running processes |

## Examples

```bash
# Development workflow
just fe-dev              # Frontend only
just be-run              # Backend only
just all                 # Both services

# Testing
just be-test             # Backend tests
just fe-test             # Frontend tests

# Custom ports
just fe-dev-port 5175   # Frontend on 5175
just be-run-port 8001   # Backend on 8001

# Kill and restart
just kill && just fe-dev
```

## Default Ports

| Service | Port |
|---------|------|
| Frontend (Vite) | 5173 |
| Backend (FastAPI) | 8000 |