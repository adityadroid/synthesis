# 021: Clear Conversation

## Phase
Phase 1 (v1.0.0)

## Description
Reset thread while keeping the conversation record.

## Requirements
- DELETE /conversations/:id/messages endpoint
- Remove all messages, keep conversation
- Optional: archive instead of delete

## Acceptance Criteria
- [ ] Messages cleared, conversation remains
- [ ] New messages can be added
- [ ] Sidebar shows empty conversation
- [ ] Original title preserved

## Dependencies
- 017: Multiple Conversations
