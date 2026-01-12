# Specification: Real-Time Live Data via WebSockets

## Overview
The dashboard currently shows stale data because the backend only fetches from external APIs when polled. This track will implement real-time data streaming using WebSockets where available, ensuring contract prices and live BTC prices update instantly.

## Bug Description
- **Current Behavior:** Data appears stale; prices don't reflect real-time market conditions.
- **Expected Behavior:** Dashboard updates instantly (<1 second) when prices change on Binance, Polymarket, or Kalshi.

## Functional Requirements

### FR1: Binance WebSocket for Live Price
- Connect to Binance WebSocket API for real-time BTC price updates.
- Binance provides `wss://stream.binance.us:9443/ws/btcusd@trade` for trade-level updates.
- Push price updates to the frontend via a backend WebSocket.

### FR2: Polymarket Live Contract Prices
- Investigate Polymarket CLOB API for WebSocket/streaming support.
- If no WebSocket is available, implement aggressive polling (every 1-2 seconds) as a fallback.

### FR3: Kalshi Live Contract Prices
- Investigate Kalshi Trade API for WebSocket/streaming support.
- If no WebSocket is available, implement aggressive polling as a fallback.

### FR4: Backend WebSocket Server
- Add a WebSocket endpoint to the FastAPI backend (e.g., `/ws/arbitrage`).
- Push aggregated live data to all connected frontend clients.

### FR5: Frontend WebSocket Client
- Replace polling (`setInterval`) with a WebSocket connection.
- Update the UI in real-time when new data arrives.

## Acceptance Criteria
- [ ] Binance BTC price updates in <1 second on the dashboard.
- [ ] Polymarket contract prices update as fast as their API allows.
- [ ] Kalshi contract prices update as fast as their API allows.
- [ ] No manual refresh needed — data streams automatically.

## Out of Scope
- Historical price charts
- Multiple cryptocurrency WebSocket streams (start with BTC only, extend later)
