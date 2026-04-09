# 057: Custom System Prompt

## Phase
Phase 2 (v1.1.0)

## Description
Set custom persona/instructions per conversation.

## Requirements
- System prompt editor
- Per-conversation setting
- Template suggestions
- Preview effect on responses

## Acceptance Criteria
- [ ] Can set system prompt
- [ ] Saves with conversation
- [ ] Affects AI responses
- [ ] Clear/reset option

## Related Files
- `src/models/conversation.py` - System prompt field
- `src/services/llm.py` - Use system prompt in context
- `frontend/src/components/Chat/SystemPromptEditor.tsx` - Editor UI

## Dependencies
- 017: Multiple Conversations
