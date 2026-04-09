# 071: File Attachments

## Phase
Phase 3 (v2.0.0)

## Description
Attach PDFs and documents for context.

## Requirements
- Document upload (PDF, TXT, DOC)
- File preview in chat
- Context injection to LLM
- File size limits

## Acceptance Criteria
- [ ] Can attach documents
- [ ] Shows file in message
- [ ] Content passed to LLM
- [ ] Handles large files

## Related Files
- `src/services/files.py` - File handling
- `src/routes/chat.py` - File upload endpoint
- `frontend/src/components/Chat/FileUploader.tsx` - Upload UI

## Dependencies
- 070: Image Uploads - Vision Support
