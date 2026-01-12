# Specification: Multi-Cryptocurrency Tab Support

## Overview
Extend the arbitrage bot dashboard to support multiple cryptocurrencies via a tabbed navigation interface. The current Bitcoin-only dashboard will become one tab among several, with preset tabs for major cryptocurrencies and a "+" button for adding custom tokens.

## Functional Requirements

### FR-1: Tab Navigation Bar
- Add a horizontal tab bar at the top of the dashboard, below the header
- Preset tabs: **Bitcoin (BTC)**, **Ethereum (ETH)**, **XRP**, **Solana (SOL)**
- Active tab should be visually highlighted
- Tab switching should NOT remount the entire page; only update data

### FR-2: Custom Token Addition (+ Button)
- A "+" button at the end of the tab bar
- Clicking "+" opens a modal/form with:
  - **Token Name** (text field, e.g., "Dogecoin")
  - **Polymarket Target** (text field for slug/URL)
  - **Kalshi Ticker** (text field for event ticker)
- After submission, a new tab appears for that custom token
- Custom tabs should persist in browser localStorage

### FR-3: Per-Tab Data Fetching
- Each tab independently fetches data from the backend
- Backend `/arbitrage` endpoint must accept an `asset` query parameter
- Data structure remains the same per asset

### FR-4: Backend Multi-Asset Support
- Parameterize `fetch_current_polymarket.py` to accept asset slug patterns
- Parameterize `fetch_current_kalshi.py` to accept different series tickers
- Known mappings:
  | Asset | Kalshi Series | Polymarket Pattern |
  |-------|---------------|-------------------|
  | BTC | KXBTCD | bitcoin-up-or-down-* |
  | ETH | KXETHDAILY | ethereum-* |
  | XRP | KXXRPDAILY | xrp-* |
  | SOL | KXSOLDDAILY | solana-* |

### FR-5: Preserve Existing Functionality
- The current BTC dashboard must remain fully functional
- All existing UI components (Best Opportunity, Market Cards, Analysis Table) should work for any asset

## Non-Functional Requirements
- Tab switching should feel instant (< 100ms visual response)
- Custom tokens should support at least 10 entries

## Acceptance Criteria
- [ ] Tab bar displays with BTC, ETH, XRP, SOL tabs
- [ ] Clicking each preset tab loads data for that cryptocurrency
- [ ] "+" button opens a modal for custom token input
- [ ] Custom tokens are saved to localStorage and persist across refreshes
- [ ] Backend `/arbitrage?asset=ETH` returns Ethereum arbitrage data
- [ ] Existing BTC functionality is unchanged

## Out of Scope
- User authentication
- Real trading execution
- Mobile-specific layouts
