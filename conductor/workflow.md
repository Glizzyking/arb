# Development Workflow

## Development Phases

### Phase 1: Planning
1. Define requirements in spec.md
2. Create implementation plan in plan.md
3. User reviews and approves plan

### Phase 2: Implementation
1. Create/modify backend code
2. Create/modify frontend code
3. Verify build passes
4. Self-test functionality

### Phase 3: Verification
1. Run automated tests (if available)
2. Visual verification via browser
3. Update walkthrough with results

## File Structure
```
conductor/
├── product.md          # Product vision and features
├── tech-stack.md       # Technology documentation
├── workflow.md         # This file
├── tracks.md           # List of all tracks
├── setup_state.json    # Setup progress state
└── tracks/             # Individual track directories
    └── <track_id>/
        ├── metadata.json
        ├── spec.md
        └── plan.md
```

## Phase Completion Verification and Checkpointing Protocol
At the end of each Phase, the agent must:
1. Verify all tasks in that phase are complete
2. Run any relevant tests
3. Document results
4. Proceed automatically if tests pass
