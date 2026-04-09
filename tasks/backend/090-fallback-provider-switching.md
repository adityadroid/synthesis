# 090: Fallback Provider Switching

## Phase
All Phases

## Description
Automatically switch providers on failure.

## Requirements
- Primary/fallback config
- Health checks
- Automatic failover
- Manual override

## Acceptance Criteria
- [ ] Switches on provider failure
- [ ] Minimal latency impact
- [ ] User notification
- [ ] Fallback to cached response

## Related Files
- `src/services/llm.py` - Provider fallback logic
- `src/config.py` - Provider configuration

## Dependencies
- 089: Retry Logic
