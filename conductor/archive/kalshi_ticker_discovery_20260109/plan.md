# Implementation Plan: Fix Kalshi Market Ticker Discovery

## Phase 1: Update KalshiClient for Real Ticker Discovery
- [ ] **Task 1.1:** Add `get_markets_by_event` method
  - Query `/markets` with `event_ticker` (date-only format)
  - Return list of all hourly markets for that day
- [ ] **Task 1.2:** Add `find_market_by_close_time` helper
  - Filter markets by target hour's `close_time`
  - Return real ticker and market data
- [ ] **Task 1.3:** Add simple cache for market discovery
  - Use dict with TTL (~5 minutes)
  - Key: `{series}_{date}`
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Update MarketURLGenerator
- [ ] **Task 2.1:** Add `generate_event_ticker` method (date-only)
  - Format: `{SERIES}-{YY}{MON}{DD}` (e.g., `KXBTCD-26JAN09`)
- [ ] **Task 2.2:** Update `generate_kalshi_url` to accept real ticker
  - Build URL from API-provided ticker instead of generated one
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Integration
- [ ] **Task 3.1:** Update `api.py` to use new discovery flow
- [ ] **Task 3.2:** Update CLI tracker to use new discovery flow
- [ ] **Task 3.3:** Verify both display correct real tickers
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Testing & Documentation
- [ ] **Task 4.1:** Test with curl that API returns real tickers
- [ ] **Task 4.2:** Visual verification of website dashboard
- [ ] **Task 4.3:** Update walkthrough with results
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
