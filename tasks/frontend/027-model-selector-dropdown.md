# 027: Model Selector Dropdown

## Phase
Phase 1 (v1.0.0)

## Description
UI dropdown to switch between available models.

## Requirements
- Dropdown with available models
- Group by provider (OpenAI, Anthropic)
- Show model info on selection
- Remember selection in session

## Acceptance Criteria
- [ ] All available models in dropdown
- [ ] Can switch models before sending
- [ ] Current selection visually indicated
- [ ] Disabled models grayed out

## Related Files
- `frontend/src/api/types.ts` - Available models type
- `frontend/src/components/Chat/ModelSelector.tsx` - Dropdown component
- `frontend/src/hooks/useModels.ts` - Available models hook
- `frontend/src/api/client.ts` - GET /models endpoint

## Dependencies
- 025: OpenAI Integration
- 026: Anthropic Integration
