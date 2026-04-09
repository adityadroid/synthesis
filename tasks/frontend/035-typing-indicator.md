# 035: Typing Indicator

## Phase
Phase 1 (v1.0.0)

## Description
Show "AI is thinking..." state during response generation.

## Requirements
- Animated indicator while waiting
- Show during API call
- Clear when response starts
- Handle long wait times

## Acceptance Criteria
- [ ] Indicator shows during request
- [ ] Animated dots/spinner
- [ ] Disappears when stream starts
- [ ] Shows error state on failure

## Related Files
- `frontend/src/hooks/useChatStream.ts` - Typing state
- `frontend/src/components/Chat/TypingIndicator.tsx` - Animated component

## Dependencies
- 007: Streaming Responses via WebSocket
