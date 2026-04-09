# 058: Temperature Slider

## Phase
Phase 2 (v1.1.0)

## Description
Adjust AI creativity/ randomness with temperature setting.

## Requirements
- Slider from 0 to 2
- Real-time display of value
- Per-conversation setting
- Default value per model

## Acceptance Criteria
- [ ] Slider controls temperature
- [ ] Shows numeric value
- [ ] Affects response style
- [ ] Persists per conversation

## Related Files
- `frontend/src/components/Chat/ModelSettings.tsx` - Temperature slider
- `frontend/src/api/types.ts` - Model settings type

## Dependencies
- 057: Custom System Prompt
