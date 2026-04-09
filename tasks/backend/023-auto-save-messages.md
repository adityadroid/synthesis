# 023: Auto-save Messages

## Phase
Phase 1 (v1.0.0)

## Description
Automatically save messages when sent.

## Requirements
- Save user message before sending to LLM
- Save LLM response after completion
- Handle partial saves on errors
- Optimistic UI updates

## Acceptance Criteria
- [ ] Message saved immediately on send
- [ ] Failed saves trigger retry
- [ ] No data loss on network errors
- [ ] UI reflects saved state

## Related Files
- `src/services/chat.py` - Message persistence in chat flow
- `src/routes/chat.py` - Auto-save in send endpoint

## Dependencies
- 006: Send Message to LLM
