# 072: Voice Input - Speech to Text

## Phase
Phase 3 (v2.0.0)

## Description
Add voice input using browser speech recognition.

## Requirements
- Microphone button
- Real-time transcription
- Edit before send
- Continuous mode option

## Acceptance Criteria
- [ ] Can record voice
- [ ] Shows transcription live
- [ ] Can edit before sending
- [ ] Works on supported browsers

## Related Files
- `frontend/src/components/Chat/VoiceInput.tsx` - Speech recognition
- `frontend/src/hooks/useSpeechToText.ts` - Browser API hook

## Dependencies
- 009: Message Display with Roles
