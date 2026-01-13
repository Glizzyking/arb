# Plan: Position Tracking Enhancements (Coin & Expiration)

## Phase 1: Planning
- [x] Task: Define requirements in spec.md
- [x] Task: Create implementation plan in plan.md
- [x] Task: User reviews and approves plan

## Phase 2: Implementation

### 2.1 Frontend: Add Coin Selection Dropdown
- [x] Task: Add `asset` field to position state/interface
- [x] Task: Create coin dropdown component (BTC, ETH, XRP, SOL)
- [x] Task: Place dropdown above "Save Position to Ledger" checkbox
- [x] Task: Display selected coin in positions table

### 2.2 Frontend: Auto-Calculated Hourly Expiration
- [x] Task: Implement `getNextFullHour()` utility function
- [x] Task: Pre-fill expiration field with next full hour on form mount
- [x] Task: Ensure expiration field remains editable
- [x] Task: Display expiration correctly in positions table

### 2.3 Backend/Database Integration
- [x] Task: Update Supabase position insert to include `asset` field
- [x] Task: Update position fetch to return `asset` field
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Task: Visual verification via browser (add position with coin & expiration)
- [x] Task: Verify positions table displays coin and expiration correctly
- [x] Task: Update walkthrough with results
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
