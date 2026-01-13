# Track: Position Tracking Enhancements (Coin & Expiration)

## Overview
Enhance the "Add Arbitrage Position" form in the tracker to include:
1. A coin/asset selector so users can specify which cryptocurrency they took the arbitrage on.
2. An auto-calculated hourly expiration, pre-filled to the next full hour but editable by the user.

## Functional Requirements

### FR1: Coin/Asset Selection
- Add a **dropdown/select menu** to the Add Position form.
- The dropdown should list all supported coins: **BTC, ETH, XRP, SOL**.
- The dropdown should be placed **right above the "Safe Position to Lenders" checkbox**.
- The selected coin should be stored with the position data.

### FR2: Hourly Expiration Auto-Fill
- The **Expiration field** should be **pre-filled** with the next full hour from the current time.
  - Example: If position is added at 3:15 PM, expiration defaults to 4:00 PM.
  - Example: If position is added at 3:00 PM, expiration defaults to 4:00 PM.
- The user can **edit** this pre-filled value if needed.
- The expiration should be stored and displayed correctly in the positions table.

## Acceptance Criteria
- [ ] Coin dropdown appears in the Add Position form above "Safe Position to Lenders".
- [ ] Dropdown lists BTC, ETH, XRP, SOL.
- [ ] Selected coin is saved and displayed in the positions table.
- [ ] Expiration field auto-fills to next full hour.
- [ ] User can override the pre-filled expiration.
- [ ] Positions table displays the coin and expiration correctly.

## Out of Scope
- Backend/database schema changes (positions are currently stored in Supabase).
- Filtering positions by coin.
