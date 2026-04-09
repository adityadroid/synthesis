# Phase Execution Skill

## Purpose
Execute all tasks within a phase systematically with inter-task consistency.

## When to Use
- Before starting a new phase (MVP, Phase 1, Phase 2, Phase 3)
- When all tasks in a phase must be completed
- For milestone delivery preparation

## Phase Reference
| Phase | Tasks | Version | Focus |
|-------|-------|---------|-------|
| MVP | 001-009 | v0.1.0 | Foundation |
| Phase 1 | 010-037 | v1.0.0 | Essential features |
| Phase 2 | 038-065 | v1.1.0 | Enhanced experience |
| Phase 3 | 066-084 | v2.0.0 | Advanced features |
| Infrastructure | 085-101 | All | Cross-cutting |

## Phase Start
1. Read phase overview in `/docs/product-roadmap.md`
2. List all tasks in phase
3. Identify task dependencies and execution order
4. Review shared infrastructure needs

## Task Execution Order
Execute tasks respecting dependencies. Tasks with no shared files can run in parallel.

## Phase-Level Concerns

### Shared Infrastructure
- Create shared modules before individual tasks
- Ensure consistent error handling across tasks
- Define shared constants/enums in common location

### Consistency
- Use same patterns across tasks in phase
- Consistent naming conventions
- Unified error responses

### Testing Strategy
- Unit tests per task
- Integration tests for task combinations
- Phase-level E2E test

## Phase Completion

### Pre-Release Checklist
- [ ] All task files marked complete
- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated
- [ ] Tests pass in CI
- [ ] Build succeeds
- [ ] Documentation updated

### Deliverables
- Working code in all layers
- Tests for all features
- Updated documentation
- Git tag for version

## Coordination
Each task within phase uses task-execution skill. Phase skill orchestrates:
1. Task ordering
2. Shared context
3. Integration between tasks
4. Phase-level verification
