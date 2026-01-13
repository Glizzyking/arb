# Product Guide: Polymarket-Kalshi Crypto Arbitrage Bot

## Initial Concept
Real-time arbitrage detection for cryptocurrency prices between Polymarket and Kalshi prediction markets.

## Project Overview
The **Polymarket-Kalshi Crypto Arbitrage Bot** is a tool designed to monitor and identify risk-free arbitrage opportunities in cryptocurrency hourly price markets between two leading prediction markets: **Polymarket** and **Kalshi**.

## Project Analysis Summary

### Technology Stack
| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.9+, FastAPI, Uvicorn, Requests, Pytz |
| **Frontend** | Next.js 16, React 19, TypeScript 5, Tailwind CSS 4 |
| **Database** | Supabase (PostgreSQL) |
| **UI Components** | shadcn/ui (Radix UI primitives), Lucide React |
| **APIs** | Polymarket CLOB API, Kalshi Trade API |

### Architecture
- **Monolithic** with separate `frontend/` and `backend/` directories
- **Backend**: FastAPI REST API serving arbitrage data at `/arbitrage` and WebSocket at `/ws/arbitrage`
- **Frontend**: Next.js App Router with real-time WebSocket connection (with REST polling fallback)

### Current Features
- Polymarket "Up/Down" hourly market data fetching (Real-time updates via WebSocket/Polling)
- Kalshi strike price market data fetching (Real-time updates via WebSocket/Polling)  
- Arbitrage detection when combined cost < $1.00 (Updated in real-time)
- Visual dashboard with opportunity highlighting and instant updates
- Direct market links for quick verification
- **[NEW] Top-level navigation** with tabs for Home Page, Positive EV, and Calculators
- **[NEW] Settings Panel** for API Key management (Polymarket and Kalshi)
- **[NEW] Dark Theme Dashboard** with premium UI elements and backdrop effects

6. **Arbitrage Tracker Enhancements**: [COMPLETED]
   - Coin selection (BTC, ETH, XRP, SOL) for position logging.
   - Auto-calculated hourly expiration defaults.
   - Enhanced UI with asset symbols and expiration tracking.

