# 037: Regenerate AI Response

## Phase
Phase 1 (v1.0.0)

## Description
Request a new AI response to the same prompt.

## Requirements
- Regenerate button on assistant messages
- Keep user message, remove assistant response
- Request new completion
- Show regenerating state

## Acceptance Criteria
- [ ] Regenerate button on AI responses
- [ ] Original prompt preserved
- [ ] Previous response replaced
- [ ] Can regenerate multiple times

## Related Files
- `frontend/src/components/Chat/Message.tsx` - Regenerate button
- `frontend/src/hooks/useChat.ts` - Regenerate logic

## Dependencies
- 006: Send Message to LLM
