# 080: Rate Limit Management

## Phase
Phase 3 (v2.0.0)

## Description
Configurable rate limits for users and workspaces.

## Requirements
- Set limits per user
- Set limits per workspace
- Tier-based defaults
- Usage tracking

## Acceptance Criteria
- [ ] Admins can set limits
- [ ] Limits enforced
- [ ] Users see usage
- [ ] Graceful degradation

## Related Files
- `src/services/rate_limit.py` - Rate limit logic
- `src/routes/admin.py` - Rate limit config endpoints

## Dependencies
- 066: Workspaces and Organizations
