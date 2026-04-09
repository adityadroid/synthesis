# 015: OAuth - Google Sign In

## Phase
Phase 1 (v1.0.0)

## Description
Add Google OAuth authentication option.

## Requirements
- OAuth 2.0 flow with Google
- Create/link account on first login
- Generate JWT on successful OAuth
- Store OAuth provider info

## Acceptance Criteria
- [ ] Redirect to Google OAuth
- [ ] Callback creates/links account
- [ ] JWT issued on success
- [ ] Existing email accounts can link Google

## Related Files
- `src/services/auth.py` - OAuth logic
- `src/routes/auth.py` - GET /auth/oauth/google, callback endpoints
- `src/config.py` - Google OAuth credentials

## Dependencies
- 002: Email/Password Login
