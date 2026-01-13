# Tracker Feature Specification

## Overview
A new "Tracker" tab in the navigation that provides a calendar-based view for logging and tracking arbitrage/spread positions across Polymarket and Kalshi. Users can record their entry prices, contract quantities, and later mark outcomes to calculate profit/loss.

## Functional Requirements

### 1. Authentication & Data Storage
- **Login Page**: Users must authenticate before accessing the Tracker
- **Supabase Backend**: All position data stored in Supabase database
- **Environment Config**: Supabase credentials configured via `.env` file
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`

### 2. Navigation
- Add "Tracker" tab in the Header navigation (next to Calculators)
- Icon: Calendar or similar tracking icon

### 3. Calendar View
- Display a monthly calendar (starting with January 2026)
- Month navigation (previous/next buttons)
- Days with tracked positions show a visual indicator (dot or badge with count)
- Clicking a day opens a side panel showing all positions for that day

### 4. Position Entry Modal
When adding a new position, user enters **two entries** (one per side):

| Field | Description |
|-------|-------------|
| **Network** | Dropdown: Polymarket or Kalshi (expandable later) |
| **Entry Price** | Price paid per contract (e.g., $0.35) |
| **Contracts** | Number of contracts purchased |
| **Expiration Hour** | Hourly expiration time (on the clock, e.g., 2:00 PM) |

- **Assumed Payout**: $1.00 per winning contract (hardcoded)
- Each tracked position consists of **two entries** (Poly side + Kalshi side)

### 5. Position Day Panel
When clicking a calendar day:
- Shows list of all positions tracked that day
- Each position card displays:
  - Network + Entry Price + Contracts (for each side)
  - Total Cost = (Poly Price × Poly Contracts) + (Kalshi Price × Kalshi Contracts)
  - Status: Pending / Resolved
  - Profit/Loss (if resolved)
- "Add New Position" button
- Click position to open resolution modal

### 6. Position Resolution
When resolving a position, user selects one outcome:

| Outcome | Result |
|---------|--------|
| **Polymarket Won** | Profit = (Poly Contracts × $1) - Total Cost |
| **Kalshi Won** | Profit = (Kalshi Contracts × $1) - Total Cost |
| **Both Lost** | Loss = -Total Cost |
| **Pending** | Not yet resolved (default) |

### 7. Profit Summary
- Monthly summary at top of Tracker page
- Shows: Total Positions, Resolved, Pending, Total Profit/Loss

## Non-Functional Requirements
- Responsive design matching existing dark theme
- Real-time sync with Supabase
- Secure authentication via Supabase Auth

## Acceptance Criteria
- [ ] User can log in and access Tracker tab
- [ ] Calendar displays current month with navigation
- [ ] User can add a new position with two entries (Poly + Kalshi)
- [ ] Positions appear on the correct calendar day
- [ ] User can mark position outcomes
- [ ] Profit/loss calculates correctly based on outcome
- [ ] Monthly summary displays accurate totals

## Out of Scope
- Automatic position detection from exchange APIs
- Multi-user/team features
- Historical data import
- Mobile app version
