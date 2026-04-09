# 019: Rename Conversation

## Phase
Phase 1 (v1.0.0)

## Description
Allow custom titles for conversation threads.

## Requirements
- PATCH /conversations/:id endpoint
- Update conversation title
- Auto-generate title from first message if empty

## Acceptance Criteria
- [ ] Can set custom title
- [ ] Title updates in sidebar immediately
- [ ] Empty title triggers auto-generation
- [ ] Only owner can rename

## Dependencies
- 017: Multiple Conversations
