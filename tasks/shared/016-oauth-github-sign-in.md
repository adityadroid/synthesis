# 016: OAuth - GitHub Sign In

## Phase
Phase 1 (v1.0.0)

## Description
Add GitHub OAuth authentication option.

## Requirements
- OAuth 2.0 flow with GitHub
- Create/link account on first login
- Generate JWT on successful OAuth
- Store OAuth provider info

## Acceptance Criteria
- [ ] Redirect to GitHub OAuth
- [ ] Callback creates/links account
- [ ] JWT issued on success
- [ ] Existing email accounts can link GitHub

## Related Files
- `src/services/auth.py` - OAuth logic
- `src/routes/auth.py` - GET /auth/oauth/github, callback endpoints

## Dependencies
- 015: OAuth - Google Sign In
