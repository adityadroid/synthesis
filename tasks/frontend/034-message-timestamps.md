# 034: Message Timestamps

## Phase
Phase 1 (v1.0.0)

## Description
Show when messages were sent and received.

## Requirements
- Store timestamp on message creation
- Display relative time (e.g., "2 min ago")
- Show absolute time on hover
- Group messages by day

## Acceptance Criteria
- [ ] Timestamps visible on messages
- [ ] Relative time format by default
- [ ] Absolute time on hover/click
- [ ] Day separators in long conversations

## Related Files
- `frontend/src/api/types.ts` - Timestamp in message type
- `frontend/src/components/Chat/Message.tsx` - Display timestamp

## Dependencies
- 009: Message Display with Roles
