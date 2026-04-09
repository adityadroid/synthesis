# 003: JWT Session Management

## Phase
MVP (v0.1.0)

## Description
Implement JWT-based authentication with refresh token rotation.

## Requirements
- Access token with short expiry (15min)
- Refresh token with longer expiry (7 days)
- Refresh token rotation on use
- Token blacklisting on logout

## Acceptance Criteria
- [ ] Access token validates correctly
- [ ] Refresh token generates new access token
- [ ] Expired tokens are rejected
- [ ] Logout invalidates refresh token

## Related Files
- `src/services/auth.py` - JWT creation/validation
- `src/routes/auth.py` - Token refresh endpoint
- `src/config.py` - JWT settings

## Dependencies
- 002: Email/Password Login
