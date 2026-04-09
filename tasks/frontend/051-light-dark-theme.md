# 051: Light/Dark Theme

## Phase
Phase 2 (v1.1.0)

## Description
Implement theme switching with system preference detection.

## Requirements
- Detect system preference
- Manual toggle option
- Persist user preference
- Smooth transition between themes

## Acceptance Criteria
- [ ] Respects system preference
- [ ] Can override with manual toggle
- [ ] Preference persists
- [ ] All UI elements themed

## Related Files
- `frontend/src/hooks/useTheme.ts` - Theme management
- `frontend/src/components/Chat/ThemeToggle.tsx` - Toggle button
- `frontend/src/index.css` - Light/dark CSS variables

## Dependencies
- 009: Message Display with Roles
