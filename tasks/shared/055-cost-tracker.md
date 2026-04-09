# 055: Cost Tracker

## Phase
Phase 2 (v1.1.0)

## Description
Estimate and display costs per conversation.

## Requirements
- Calculate cost per message
- Sum conversation costs
- Use current pricing rates
- Show in conversation info

## Acceptance Criteria
- [ ] Estimates costs accurately
- [ ] Per-conversation totals
- [ ] Rates configurable
- [ ] Updates with model changes

## Related Files
- `src/config.py` - Model pricing rates
- `src/services/usage.py` - Cost calculation

## Dependencies
- 054: Token Counter
