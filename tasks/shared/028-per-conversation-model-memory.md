# 028: Per-Conversation Model Memory

## Phase
Phase 1 (v1.0.0)

## Description
Remember model selection for each conversation thread.

## Requirements
- Store selected model per conversation
- Load conversation's preferred model on open
- Default to user's preferred model

## Acceptance Criteria
- [ ] Model persists with conversation
- [ ] Opening conversation sets correct model
- [ ] Can override per conversation
- [ ] User default for new conversations

## Related Files
- `src/models/conversation.py` - Add model_id field
- `src/services/conversation.py` - Load/save model selection
- `src/services/chat.py` - Use conversation's model

## Dependencies
- 017: Multiple Conversations
- 027: Model Selector Dropdown
