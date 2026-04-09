# 038: Edit User Messages

## Phase
Phase 2 (v1.1.0)

## Description
Allow editing of already-sent user messages.

## Requirements
- Edit button on user messages
- Inline editing interface
- Save/Cancel actions
- Re-generate AI response with edited prompt

## Acceptance Criteria
- [ ] Can edit own messages
- [ ] Inline editing UI
- [ ] Saves and shows edited version
- [ ] Triggers new AI response

## Related Files
- `src/models/chat.py` - Message update schema
- `src/services/chat.py` - Update message logic
- `src/routes/chat.py` - PATCH /chat/messages/:id endpoint

## Dependencies
- 009: Message Display with Roles
