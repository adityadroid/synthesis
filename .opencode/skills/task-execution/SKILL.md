# Task Execution Skill

## Purpose
Execute individual tasks with completeness and quality assurance.

## When to Use
- Before starting any task from `/tasks/`
- When a task requires multiple files or layers
- When verification and testing are required

## Pre-Execution
1. Read the task markdown file at `/tasks/{XXX}-{name}.md`
2. List all dependencies and verify they are complete
3. Identify affected files from "Related Files" section
4. Review any existing code in affected areas

## Implementation
1. Follow clean architecture layers:
   - `domain/` - Pure business logic, zero external imports
   - `application/` - Use cases, domain imports only
   - `infrastructure/` - External implementations
   - `presentation/` - API/CLI handlers

2. For each requirement:
   - Implement the feature
   - Add error handling
   - Include logging context
   - Use type hints

3. Layer Compliance Check:
   ```
   presentation → application → domain ← infrastructure
   ```

## Testing
1. Write unit tests for domain logic
2. Write integration tests for repositories
3. Verify tests pass before completing

## Verification
1. Review acceptance criteria one-by-one
2. Run `lsp_diagnostics` for errors
3. Verify all checklist items below
4. Check for any TODOs or placeholders

## Completeness Checklist
- [ ] All requirements implemented
- [ ] All acceptance criteria met
- [ ] Tests written/passed
- [ ] Layer compliance verified
- [ ] Documentation updated
- [ ] No TODOs or placeholders

## Post-Execution
1. Mark acceptance criteria as complete in task file
2. Update related documentation if needed
3. Note any follow-up tasks or improvements
