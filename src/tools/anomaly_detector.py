"""
Statistical Anomaly Detection Engine for MarketSentry Sentinel.
Calculates volatility z-scores, volume surges, and price velocity anomalies using yfinance.
"""
from typing import Dict, Any, List, Optional
import yfinance as yf
import pandas as pd
import numpy as np


class MarketSentinel:
    def __init__(self, volume_threshold: float = 1.8, z_score_threshold: float = 2.0):
        self.volume_threshold = volume_threshold
        self.z_score_threshold = z_score_threshold

    def scan_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Scans a single ticker for statistical anomalies in price and volume.
        """
        try:
            stock = yf.Ticker(ticker.strip().upper())
            # Fetch 30 days of 1-day interval historical bars
            hist = stock.history(period="1mo", interval="1d")
            
            if hist.empty or len(hist) < 10:
                return {"ticker": ticker, "is_anomaly": False, "reason": "Insufficient historical data"}

            # Calculate daily returns and rolling volatility
            hist['Daily_Return'] = hist['Close'].pct_change()
            mean_return = hist['Daily_Return'].mean()
            std_return = hist['Daily_Return'].std()

            latest_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            latest_return = (latest_close - prev_close) / prev_close

            # Price Return Z-Score
            z_score = (latest_return - mean_return) / (std_return if std_return != 0 else 1e-6)

            # Volume Surge Ratio
            avg_volume_20d = hist['Volume'].iloc[-21:-1].mean()
            latest_volume = hist['Volume'].iloc[-1]
            volume_ratio = latest_volume / avg_volume_20d if avg_volume_20d > 0 else 1.0

            # Evaluate Anomaly Triggers
            is_price_anomaly = abs(z_score) >= self.z_score_threshold
            is_volume_surge = volume_ratio >= self.volume_threshold

            is_anomaly = is_price_anomaly or is_volume_surge
            triggers = []

            if is_price_anomaly:
                direction = "SPIKE" if z_score > 0 else "DROP"
                triggers.append(f"Abnormal Price {direction} (Z-Score: {z_score:.2f}, Return: {latest_return*100:+.2f}%)")

            if is_volume_surge:
                triggers.append(f"High Volume Outlier ({volume_ratio:.2f}x of 20-day avg volume)")

            return {
                "ticker": ticker.upper(),
                "is_anomaly": is_anomaly,
                "latest_price": round(float(latest_close), 2),
                "latest_return_pct": round(float(latest_return * 100), 2),
                "z_score": round(float(z_score), 2),
                "volume_ratio": round(float(volume_ratio), 2),
                "triggers": triggers
            }

        except Exception as e:
            return {"ticker": ticker, "is_anomaly": False, "error": str(e)}

    def scan_watchlist(self, watchlist: List[str]) -> List[Dict[str, Any]]:
        """Scans a collection of tickers and isolates anomalous events."""
        anomalies = []
        for sym in watchlist:
            result = self.scan_ticker(sym)
            if result.get("is_anomaly"):
                anomalies.append(result)
        return anomalies