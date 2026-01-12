# Specification: Fix Polymarket/Kalshi Time Offset Mismatch

## Overview
Polymarket and Kalshi use different naming conventions for their hourly crypto markets. Currently, both are using `hours_offset=1`, which causes a mismatch. Polymarket should use `hours_offset=0` to target the current hour's market name (which closes at the *next* hour).

## Bug Description
- **Root Cause:** The previous fix applied `hours_offset=1` to both Polymarket and Kalshi.
- **Polymarket Naming:** "3pm" market = Opens at 3pm, closes at 4pm (named by *opening* hour)
- **Kalshi Naming:** "1016" market = Closes at 4pm (named by *closing* hour)
- **Current Behavior:** At 3:30 PM, Polymarket targets "4pm" slug, Kalshi targets "4pm (1016)" ticker.
- **Expected Behavior:** At 3:30 PM, Polymarket should target "3pm" slug, Kalshi should target "4pm (1016)" ticker. Both represent the same market window.

## Functional Requirements

### FR1: Use Different Offsets Per Platform
- Polymarket: Use `hours_offset=0` in `MarketURLGenerator.get_market_pair()` for slug generation.
- Kalshi: Continue using `hours_offset=1` for ticker discovery.
- Applies to all cryptocurrencies (BTC, ETH, XRP, SOL) and custom tokens.

### FR2: Do Not Change Kalshi Logic
- Kalshi is working correctly. Do not modify the Kalshi ticker generation.

## Acceptance Criteria
- [ ] At 3:30 PM, Polymarket slug shows "3pm" (not "4pm")
- [ ] At 3:30 PM, Kalshi ticker shows "1016" (4pm close) — unchanged
- [ ] Clicking Polymarket link opens the correct market page
- [ ] Applies to all assets (BTC, ETH, etc.)

## Out of Scope
- Changing Kalshi logic
- Adding configurable offsets via UI
