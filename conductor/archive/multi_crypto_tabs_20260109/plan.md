# Implementation Plan: Multi-Cryptocurrency Tab Support

## Phase 1: Backend Multi-Asset Support
Extend the backend to handle multiple cryptocurrencies.

### Tasks
- [ ] **Task 1.1:** Create `backend/asset_config.py` with asset mappings
  - Define ASSET_CONFIG dict with Kalshi tickers and Polymarket patterns
  - Include BTC, ETH, XRP, SOL defaults
- [ ] **Task 1.2:** Parameterize `fetch_current_kalshi.py`
  - Add `series_ticker` parameter to `fetch_kalshi_data_struct()`
  - Update URL generation to use configurable ticker
- [ ] **Task 1.3:** Parameterize `fetch_current_polymarket.py`
  - Add `slug_pattern` parameter to `fetch_polymarket_data_struct()`
  - Update market URL generation for different assets
- [ ] **Task 1.4:** Update `api.py` endpoint
  - Add `asset` query parameter to `/arbitrage`
  - Route to correct fetchers based on asset
  - Default to "BTC" for backward compatibility
- [ ] **Task 1.5:** Verify backend changes
  - Test `/arbitrage?asset=BTC` returns data
  - Test `/arbitrage?asset=ETH` returns data (or appropriate error if no market)

---

## Phase 2: Frontend Tab Component
Create the tab navigation UI.

### Tasks
- [ ] **Task 2.1:** Create `TabNavigation` component
  - Create `frontend/components/TabNavigation.tsx`
  - Render horizontal tabs with preset assets
  - Handle active state styling
- [ ] **Task 2.2:** Add "+" button and modal
  - Create `AddTokenModal.tsx` component
  - Include form fields: Token Name, Polymarket Target, Kalshi Ticker
  - Wire up form submission
- [ ] **Task 2.3:** Implement localStorage persistence
  - Save custom tokens to localStorage key `custom_tokens`
  - Load custom tokens on page mount
  - Render custom token tabs dynamically

---

## Phase 3: Dashboard Integration
Wire tabs to the dashboard data flow.

### Tasks
- [ ] **Task 3.1:** Refactor `page.tsx` to use tabs
  - Add `activeAsset` state
  - Pass asset to API fetch URL
  - Render TabNavigation at top
- [ ] **Task 3.2:** Update fetch URL
  - Change from `/arbitrage` to `/arbitrage?asset=${activeAsset}`
  - Update on tab change
- [ ] **Task 3.3:** Handle custom token fetching
  - For custom tokens, pass user-provided slug/ticker to backend
  - Add `/arbitrage/custom` endpoint if needed

---

## Phase 4: Testing & Verification
Ensure all functionality works end-to-end.

### Tasks
- [ ] **Task 4.1:** Browser verification
  - Verify BTC tab loads existing functionality
  - Verify other preset tabs attempt to load
  - Verify "+" modal works and saves tokens
- [ ] **Task 4.2:** Update walkthrough
  - Document new features with screenshots

---

## Verification Plan

### Automated Tests
- Backend: Hit `/arbitrage?asset=BTC` and verify response structure
- Backend: Hit `/arbitrage?asset=ETH` and verify response or error handling

### Manual Verification
- Visual confirmation of tab bar in browser
- Click through all preset tabs
- Add a custom token via "+" and verify persistence after refresh
