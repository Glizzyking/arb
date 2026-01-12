# Specification: Integrate Tracker Module into Website API

## Overview
Replace the existing data fetching logic in `backend/api.py` with the working `backend/tracker/` module. This ensures the website uses the correct Kalshi event ticker format (`KXBTCD-26JAN0922`) and Polymarket slug generation that was verified working in the CLI tracker.

## Functional Requirements

### FR-1: Replace API Data Fetching
- The `/arbitrage` endpoint in `api.py` must use `tracker.market_generator.MarketURLGenerator` for ticker/slug generation
- The `/arbitrage` endpoint must use `tracker.api_clients.CombinedMarketFetcher` for data fetching
- The endpoint must use `tracker.config.CRYPTO_CONFIGS` for multi-crypto support

### FR-2: Maintain Response Format
- The API response structure must remain unchanged to avoid frontend modifications
- Adapt tracker output to match the existing response format expected by the frontend

### FR-3: Remove Old Fetchers
- Delete `backend/fetch_current_kalshi.py` (no longer needed)
- Delete `backend/fetch_current_polymarket.py` (no longer needed)
- Remove any unused imports from `api.py`

## Acceptance Criteria
- [ ] Website dashboard displays live Kalshi data (not "Market missing")
- [ ] Website dashboard displays live Polymarket data
- [ ] All 4 cryptocurrencies (BTC, ETH, XRP, SOL) work correctly
- [ ] Old fetcher files are deleted
- [ ] No frontend changes required

## Out of Scope
- Frontend UI changes
- Adding new cryptocurrencies
- Authentication for Kalshi trading
