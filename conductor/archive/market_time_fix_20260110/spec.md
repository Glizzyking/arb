# Specification: Fix Market Time Selection - Target Next Hour

## Overview
The bot currently targets the **current hour's market** (e.g., at 2:30 PM, it shows the 2pm market). This is incorrect behavior. The correct behavior is to always target the **next hour's market** because traders bet on where the price will be at the next hour's close, not the current one.

## Bug Description
- **Current Behavior:** At 2:30 PM, the bot shows the "2pm" market (opened at 2pm, closes at 3pm)
- **Expected Behavior:** At 2:30 PM, the bot should show the "3pm" market (opens at 3pm, closes at 4pm)

## Root Cause
In `api.py`, the code calls `get_target_hours(0)` which returns the current hour's market window. It should call `get_target_hours(1)` to get the next hour's market.

## Functional Requirements

### FR1: Update API Time Logic
- Change `get_target_hours(0)` to `get_target_hours(1)` in the `/arbitrage` endpoint
- Change the same in the `/arbitrage/custom` endpoint (if applicable)
- This shifts the target from "current hour" to "next hour"

### FR2: Keep Behavior Simple
- Always target the next hour, even at x:59 (no special edge case handling)

## Acceptance Criteria
- [ ] At 2:30 PM, the dashboard shows the 3pm market (not 2pm)
- [ ] At 2:59 PM, the dashboard still shows the 3pm market
- [ ] Polymarket slug correctly reflects the next hour
- [ ] Kalshi ticker correctly reflects the next hour

## Out of Scope
- Adding a toggle for "current" vs "next" hour
- Complex edge-case handling near market close
