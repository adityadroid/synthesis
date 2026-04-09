# 004: Logout

## Phase
MVP (v0.1.0)

## Description
Clear user session and invalidate tokens.

## Requirements
- Invalidate refresh token
- Clear client-side tokens
- Log session end

## Acceptance Criteria
- [ ] Refresh token is blacklisted
- [ ] Subsequent refresh attempts fail
- [ ] Returns success confirmation

## Related Files
- `src/services/auth.py` - Token invalidation logic
- `src/routes/auth.py` - POST /auth/logout endpoint

## Dependencies
- 003: JWT Session Management
