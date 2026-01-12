# Implementation Plan: Fix Market Time Selection - Target Next Hour

## Phase 1: Planning
- [x] Define requirements in spec.md
- [x] Create implementation plan in plan.md
- [x] User reviews and approves plan

## Phase 2: Implementation

### Task 1: Update /arbitrage Endpoint
- [x] Locate `get_target_hours(0)` calls in `api.py`
- [x] Change to `get_target_hours(1)` for next hour targeting
- [x] Update `get_market_pair()` call to use offset of 1

### Task 2: Update /arbitrage/custom Endpoint
- [x] Verify if custom endpoint uses same time logic
- [x] Apply same fix if needed

- [x] Task 3: Verify Build
- [x] Ensure backend starts without errors
- [x] Test API response returns next hour's market

- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Verification

### Task 1: Visual Verification via Browser
- [x] Navigate to dashboard at `http://localhost:3000`
- [x] Verify Polymarket slug shows next hour (e.g., 3pm at 2:30 PM)
- [x] Verify Kalshi ticker shows next hour
- [x] Click market links to confirm correct pages open

### Task 2: Update Walkthrough
- [x] Document the fix
- [x] Include verification screenshot

- [x] Task: Conductor - User Manual Verification 'Phase 3: Verification' (Protocol in workflow.md)
