# Implementation Plan: Integrate Tracker Module into Website API

## Phase 1: Backend Integration
- [ ] **Task 1.1:** Update `api.py` imports to include tracker module
  - Import MarketURLGenerator, CombinedMarketFetcher, CRYPTO_CONFIGS
- [ ] **Task 1.2:** Refactor `/arbitrage` endpoint
  - Replace old fetcher calls with tracker module
  - Generate event tickers using MarketURLGenerator
  - Fetch data using CombinedMarketFetcher
- [ ] **Task 1.3:** Adapt response format
  - Map tracker output to existing frontend-expected format
  - Ensure backward compatibility
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Cleanup
- [ ] **Task 2.1:** Delete old fetcher files
  - Remove `backend/fetch_current_kalshi.py`
  - Remove `backend/fetch_current_polymarket.py`
- [ ] **Task 2.2:** Remove unused imports from `api.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Verification
- [ ] **Task 3.1:** Restart backend and test `/arbitrage` endpoint
- [ ] **Task 3.2:** Verify website dashboard shows Kalshi data
- [ ] **Task 3.3:** Verify all 4 cryptocurrencies work
- [ ] **Task 3.4:** Update walkthrough with results
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
