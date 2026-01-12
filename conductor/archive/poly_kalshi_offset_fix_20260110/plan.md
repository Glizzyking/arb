# Implementation Plan: Fix Polymarket/Kalshi Time Offset Mismatch

## Phase 1: Planning
- [x] Define requirements in spec.md
- [x] Create implementation plan in plan.md
- [x] User reviews and approves plan

## Phase 2: Implementation

### Task 1: Refactor get_market_pair() in market_generator.py
- [x] Modify the `get_market_pair()` method to use different offsets for Polymarket vs Kalshi
- [x] Kalshi uses hours_offset=1 for ticker discovery (next hour close)
- [x] Polymarket uses hours_offset=0 for slug generation (current hour open)

### Task 2: Update api.py to Use Correct Offsets
- [x] Update `/arbitrage` endpoint to pass the correct offset logic (handled in generator)
- [x] Update `/arbitrage/custom` endpoint similarly (handled in generator)

### Task 3: Verify Build
- [x] Ensure backend starts without errors
- [x] Test API response returns correct Polymarket slug (current hour name) and Kalshi ticker (next hour close)

- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Verification

### Task 1: Visual Verification via Browser
- [x] Navigate to dashboard at `http://localhost:3000`
- [x] Verify Polymarket slug shows current hour name (e.g., "3pm" at 3:30 PM)
- [x] Verify Kalshi ticker shows next hour close (e.g., "1016" for 4pm at 3:30 PM)
- [x] Click market links to confirm correct pages open

### Task 2: Update Walkthrough
- [x] Document the fix
- [x] Include verification screenshot

- [x] Task: Conductor - User Manual Verification 'Phase 3: Verification' (Protocol in workflow.md)
