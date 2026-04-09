# 031: Code Syntax Highlighting

## Phase
Phase 1 (v1.0.0)

## Description
Apply language-specific coloring to code blocks.

## Requirements
- Detect programming language
- Apply syntax highlighting
- Support common languages (JS, Python, Go, etc.)
- Theme-consistent colors

## Acceptance Criteria
- [ ] Code blocks have syntax highlighting
- [ ] Language auto-detected
- [ ] Consistent with app theme
- [ ] Copy button on code blocks

## Related Files
- `frontend/src/components/Chat/MessageContent.tsx` - Add syntax highlighting
- `frontend/package.json` - Add react-syntax-highlighter

## Dependencies
- 030: Markdown Rendering
