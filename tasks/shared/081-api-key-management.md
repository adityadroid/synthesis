# 081: API Key Management

## Phase
Phase 3 (v2.0.0)

## Description
Personal API keys for external programmatic access.

## Requirements
- Generate API keys
- Scope control
- Usage tracking per key
- Revoke keys

## Acceptance Criteria
- [ ] Can generate keys
- [ ] Keys have scopes
- [ ] Usage tracked per key
- [ ] Can revoke keys

## Related Files
- `src/services/auth.py` - API key generation
- `src/routes/auth.py` - API key endpoints
- `src/config.py` - API key settings

## Dependencies
- 066: Workspaces and Organizations
