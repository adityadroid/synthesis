# 091: Health Check Endpoints

## Phase
All Phases

## Description
API health endpoints for monitoring.

## Requirements
- GET /health basic
- GET /health/detailed with checks
- Database connectivity
- External service status

## Acceptance Criteria
- [ ] Health endpoint responds
- [ ] Shows all dependencies
- [ ] 200 when healthy
- [ ] 503 when unhealthy

## Related Files
- `src/routes/health.py` - Health check endpoints
- `src/db.py` - Database health check

## Dependencies
- 006: Send Message to LLM
