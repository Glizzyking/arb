"""
Configuration for Crypto Hourly Market Tracker
Easily add new cryptocurrencies by following the pattern below.
"""

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class CryptoConfig:
    """Configuration for a single cryptocurrency across both platforms"""
    name: str
    symbol: str
    
    # Kalshi configuration
    kalshi_series: str           # e.g., "KXBTCD" for Bitcoin
    kalshi_market_base: str      # e.g., "kxbtcd" (lowercase for ticker)
    
    # Polymarket configuration
    polymarket_slug_prefix: str  # e.g., "bitcoin-up-or-down"
    
    # Resolution source (optional, for verification)
    binance_symbol: Optional[str] = "BTCUSD"


# ============================================================================
# ADD NEW CRYPTOCURRENCIES HERE
# ============================================================================
CRYPTO_CONFIGS: Dict[str, CryptoConfig] = {
    "BTC": CryptoConfig(
        name="Bitcoin",
        symbol="BTC",
        kalshi_series="KXBTCD",
        kalshi_market_base="kxbtcd",
        polymarket_slug_prefix="bitcoin-up-or-down",
        binance_symbol="BTCUSD"
    ),
    "ETH": CryptoConfig(
        name="Ethereum", 
        symbol="ETH",
        kalshi_series="KXETHD",
        kalshi_market_base="kxethd",
        polymarket_slug_prefix="ethereum-up-or-down",
        binance_symbol="ETHUSD"
    ),
    "XRP": CryptoConfig(
        name="XRP",
        symbol="XRP",
        kalshi_series="KXXRPD",
        kalshi_market_base="kxxrpd",
        polymarket_slug_prefix="xrp-up-or-down",
        binance_symbol="XRPUSD"
    ),
    "SOL": CryptoConfig(
        name="Solana",
        symbol="SOL",
        kalshi_series="KXSOLD",
        kalshi_market_base="kxsold",
        polymarket_slug_prefix="solana-up-or-down",
        binance_symbol="SOLUSD"
    ),
}

# ============================================================================
# API ENDPOINTS
# ============================================================================
KALSHI_API_BASE = "https://api.elections.kalshi.com/trade-api/v2"
POLYMARKET_GAMMA_API = "https://gamma-api.polymarket.com"
POLYMARKET_CLOB_API = "https://clob.polymarket.com"

# ============================================================================
# TRADING SETTINGS
# ============================================================================
DEFAULT_SETTINGS = {
    "min_arb_percent": 2.0,           # Minimum arbitrage % to alert
    "kalshi_fee_rate": 0.01,          # 1% Kalshi fee
    "polymarket_fee_rate": 0.02,      # 2% Polymarket fee
    "scan_interval_seconds": 60,      # How often to check for opportunities
    "timezone": "US/Eastern",         # EST/EDT for market times
}
