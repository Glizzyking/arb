# Implementation Plan: Fix Asset Switching Race Condition

## Phase 1: Fix Polling Logic
- [x] **Task 1.1:** Add AbortController to cancel in-flight requests
  - Create AbortController ref in Dashboard component
  - Pass signal to fetch() calls
  - Abort previous controller on asset change
- [x] **Task 1.2:** Fix stale closure in useEffect
  - Use useRef to track current activeAsset
  - Update ref before fetch, check ref in fetch callback
  - Clear interval properly on asset change
- [x] **Task 1.3:** Clear data on asset switch
  - Set data to null when activeAsset changes
  - Ensure loading state is set to true
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Verification
- [x] **Task 2.1:** Test asset switching in browser
  - Switch BTC → ETH, verify only ETH requests in backend logs
  - Switch ETH → XRP → SOL rapidly, verify no race conditions
- [x] **Task 2.2:** Update walkthrough with results
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

