# Specification: Backend Tracker Module Refactor

## Overview
Add a new modular Python tracker system with proper API clients, smart URL generators 
based on time/timezone, and CryptoConfig system. The key insight is handling the 
different identifier formats between platforms:
- **Kalshi:** `{base}-{YY}{mon}{DD}{HH}` (24h) → `kxbtcd-26jan0921`
- **Polymarket:** `{crypto}-up-or-down-{month}-{day}-{hour}{am/pm}-et` → `bitcoin-up-or-down-january-9-9pm-et`

## Module Specifications

### 1. `config.py`
- **CryptoConfig dataclass** with fields:
  - `name`, `symbol`, `kalshi_series`, `kalshi_market_base`
  - `polymarket_slug_prefix`, `binance_pair`
- **CRYPTO_CONFIGS dict** with BTC and ETH pre-configured
- **API endpoints:** `KALSHI_API_BASE`, `POLYMARKET_GAMMA_API`, `POLYMARKET_CLOB_API`
- **DEFAULT_SETTINGS:** `min_arb_percent=2.0`, `scan_interval_seconds=60`, `timezone=US/Eastern`

### 2. `market_generator.py` (MarketURLGenerator class)
- `get_current_time()` — Returns timezone-aware datetime (US/Eastern)
- `get_target_hours(offset)` — Get market window start/end times
- `get_next_tradeable_market()` — Skip current if past minute 55
- `generate_kalshi_ticker(crypto, time)` → `kxbtcd-26jan0921`
- `generate_kalshi_url(crypto, time)` → Full Kalshi URL
- `generate_polymarket_slug(crypto, time)` → `bitcoin-up-or-down-january-9-9pm-et`
- `generate_polymarket_url(crypto, time)` → Full Polymarket URL
- `get_market_pair(crypto, offset)` — Combined info for both platforms
- `get_all_active_markets(cryptos)` — All current/next hour markets

### 3. `api_clients.py`
**KalshiClient class:**
- `get_market(ticker)` — Fetch market by ticker
- `get_markets_by_series(series_ticker, status)` — All markets in series
- `get_orderbook(ticker)` — Fetch orderbook
- `get_best_prices(ticker)` — Returns yes_bid, yes_ask, no_bid, no_ask

**PolymarketClient class:**
- `get_event_by_slug(slug)` — Fetch event data
- `get_markets_by_event_slug(slug)` — All markets for event
- `search_crypto_events(prefix, active_only)` — Search by slug prefix
- `get_market_prices(slug)` — Get Up/Down prices

**CombinedMarketFetcher class:**
- `fetch_market_pair(kalshi_ticker, poly_slug)` — Combined data
- `_calculate_arbitrage(kalshi, poly)` — Detect arb opportunities

### 4. `tracker.py` (CLI)
- `--list` — Show current market URLs
- `--once` — Single arbitrage scan
- `--interval N` — Continuous monitoring every N seconds
- `--json` — JSON output for integration
- `--add SYMBOL` — Instructions for adding new crypto

## Arbitrage Logic
Opportunity exists when:
```
Kalshi YES Ask + Polymarket DOWN < $1.00
   OR
Kalshi NO Ask + Polymarket UP < $1.00
```

## Acceptance Criteria
- [ ] All 4 modules created in `backend/tracker/`
- [ ] `python -m tracker --list` shows correct URLs for current hour
- [ ] Time-based ticker generation matches actual platform URLs
- [ ] Arbitrage calculation identifies opportunities correctly
- [ ] Can add new crypto by editing only `config.py`

## Out of Scope
- Frontend integration (Phase 2)
- Automated trade execution
- Historical data storage
