# Implementation Plan: Backend Tracker Module Refactor

## Phase 1: Create Module Structure
- [x] **Task 1.1:** Create `backend/tracker/` directory with `__init__.py`
- [x] **Task 1.2:** Create `backend/tracker/config.py`
  - CryptoConfig dataclass
  - CRYPTO_CONFIGS dict (BTC, ETH)
  - API endpoints and DEFAULT_SETTINGS
- [x] **Task 1.3:** Add pytz to requirements.txt
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Market URL Generator
- [x] **Task 2.1:** Create `backend/tracker/market_generator.py`
  - MarketURLGenerator class
  - Month name mappings (abbr and full)
  - get_current_time(), get_target_hours()
  - get_next_tradeable_market() with minute 55 logic
- [x] **Task 2.2:** Implement Kalshi ticker generation
  - generate_kalshi_ticker() → `kxbtcd-26jan0921`
  - generate_kalshi_url()
- [x] **Task 2.3:** Implement Polymarket slug generation
  - generate_polymarket_slug() → `bitcoin-up-or-down-january-9-9pm-et`
  - generate_polymarket_url()
  - 12-hour AM/PM conversion
- [x] **Task 2.4:** Implement combined helpers
  - get_market_pair()
  - get_all_active_markets()
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: API Clients
- [x] **Task 3.1:** Create `backend/tracker/api_clients.py`
- [x] **Task 3.2:** Implement KalshiClient
  - get_market(), get_markets_by_series()
  - get_orderbook(), get_best_prices()
- [x] **Task 3.3:** Implement PolymarketClient
  - get_event_by_slug(), get_markets_by_event_slug()
  - search_crypto_events(), get_market_prices()
- [x] **Task 3.4:** Implement CombinedMarketFetcher
  - fetch_market_pair()
  - _calculate_arbitrage() with both strategies
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: CLI Tracker
- [x] **Task 4.1:** Create `backend/tracker/cli.py` (renamed to avoid module shadowing)
  - CryptoMarketTracker class
  - ArgumentParser with --list, --once, --interval, --json, --add
- [x] **Task 4.2:** Implement core methods
  - get_current_market_status()
  - scan_for_arbitrage()
  - get_next_tradeable_market()
  - run_continuous()
- [x] **Task 4.3:** Test CLI commands
  - `python -m tracker.cli --list`
  - `python -m tracker.cli --once`
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5: Verification
- [x] **Task 5.1:** Verify ticker generation matches real platform URLs
- [x] **Task 5.2:** Verify API clients return valid data
- [x] **Task 5.3:** Update walkthrough with results
- [x] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)
