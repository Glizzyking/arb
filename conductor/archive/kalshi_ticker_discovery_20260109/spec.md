# Specification: Fix Kalshi Market Ticker Discovery

## Overview
The current implementation generates Kalshi event tickers (e.g., `KXBTCD-26JAN0923`) based on assumptions about the format. This is incorrect — Kalshi's API requires querying by **date-only event ticker** (e.g., `KXBTCD-26JAN09`) and then filtering by `close_time` to find the real market ticker.

## Root Cause
```
Current (Wrong):   Generate → KXBTCD-26JAN0923 → Query API → May fail
Correct:           Query → KXBTCD-26JAN09 → Filter by close_time → Get real ticker
```

## Functional Requirements

### FR-1: Query by Date-Only Event Ticker
- Generate event ticker without hour: `{SERIES}-{YY}{MON}{DD}` (e.g., `KXBTCD-26JAN09`)
- Query Kalshi `/markets` endpoint with `event_ticker` parameter
- Receive list of all hourly markets for that day

### FR-2: Filter by Target Hour
- Parse `close_time` from each returned market
- Match market where `close_time.hour == target_hour`
- Extract the real `ticker` from API response

### FR-3: Add Market Discovery Caching
- Cache the day's market list for ~5 minutes to reduce API calls
- Key: `{series}_{date}` (e.g., `KXBTCD_26JAN09`)
- Invalidate cache when date changes

### FR-4: Update Both API and CLI
- Apply fix to `KalshiClient` in `tracker/api_clients.py`
- Both `api.py` and `tracker/cli.py` will benefit automatically

### FR-5: Build URLs from Real Ticker
- Construct Kalshi URL using the real ticker from API
- Format: `https://kalshi.com/markets/{series.lower()}/.../{ticker.lower()}`

## Acceptance Criteria
- [ ] API returns real Kalshi tickers from the API, not generated ones
- [ ] CLI tracker displays correct market data
- [ ] Market discovery is cached for 5 minutes
- [ ] No "Market not found" errors for valid hourly markets

## Out of Scope
- Polymarket slug generation (already working correctly)
- Adding new cryptocurrencies
