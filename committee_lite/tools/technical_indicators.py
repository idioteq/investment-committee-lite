"""Technical indicators calculator."""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any


def get_technical_indicators(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """
    Calculate technical indicators for a ticker.

    Args:
        ticker: Stock ticker symbol
        period: Historical period ("1y", "6mo", "3mo", etc.)

    Returns:
        Dictionary containing technical indicators
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"ticker": ticker, "error": "No price data available"}

        # Current price
        current_price = hist['Close'].iloc[-1]

        # Moving averages
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]

        # RSI (14-day)
        rsi = calculate_rsi(hist['Close'], period=14)

        # MACD
        macd_line, signal_line, histogram = calculate_macd(hist['Close'])

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(hist['Close'])

        # Volatility
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized

        # Price statistics
        high_52w = hist['Close'].max()
        low_52w = hist['Close'].min()
        avg_volume = hist['Volume'].mean()

        # Support/resistance (simple heuristic: recent highs/lows)
        recent_30d = hist['Close'].tail(30)
        resistance = recent_30d.quantile(0.75)
        support = recent_30d.quantile(0.25)

        return {
            "ticker": ticker,
            "current_price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi": rsi,
            "macd": macd_line,
            "macd_signal": signal_line,
            "macd_histogram": histogram,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "volatility_annual": volatility,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "avg_volume": avg_volume,
            "support": support,
            "resistance": resistance,
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e)
        }


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate Relative Strength Index."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD indicator."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Calculate Bollinger Bands."""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()

    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)

    return upper_band.iloc[-1], sma.iloc[-1], lower_band.iloc[-1]


def format_technical_summary(data: Dict[str, Any]) -> str:
    """Format technical indicators into readable summary."""
    if "error" in data:
        return f"Error fetching technical data for {data['ticker']}: {data['error']}"

    def fmt(value):
        if value is None or pd.isna(value):
            return "N/A"
        return f"{value:.2f}"

    # Determine trend
    price = data.get('current_price', 0)
    sma_20 = data.get('sma_20', 0)
    sma_50 = data.get('sma_50', 0)
    sma_200 = data.get('sma_200', 0)

    if price > sma_20 > sma_50 > sma_200:
        trend = "STRONG UPTREND"
    elif price > sma_50 > sma_200:
        trend = "Uptrend"
    elif price < sma_20 < sma_50 < sma_200:
        trend = "STRONG DOWNTREND"
    elif price < sma_50 < sma_200:
        trend = "Downtrend"
    else:
        trend = "Sideways/Mixed"

    # RSI interpretation
    rsi = data.get('rsi', 50)
    if rsi > 70:
        rsi_status = "OVERBOUGHT"
    elif rsi < 30:
        rsi_status = "OVERSOLD"
    else:
        rsi_status = "Neutral"

    # MACD interpretation
    macd = data.get('macd', 0)
    signal = data.get('macd_signal', 0)
    macd_status = "Bullish" if macd > signal else "Bearish"

    lines = [
        f"Technical Analysis: {data['ticker']}",
        f"Current Price: ${fmt(price)}",
        "",
        "TREND:",
        f"  Status: {trend}",
        f"  20-SMA: ${fmt(sma_20)}",
        f"  50-SMA: ${fmt(sma_50)}",
        f"  200-SMA: ${fmt(sma_200)}",
        "",
        "MOMENTUM:",
        f"  RSI: {fmt(rsi)} ({rsi_status})",
        f"  MACD: {fmt(macd)} ({macd_status})",
        f"  Signal: {fmt(signal)}",
        "",
        "VOLATILITY & LEVELS:",
        f"  Annual Volatility: {fmt(data.get('volatility_annual', 0) * 100)}%",
        f"  52-Week High: ${fmt(data.get('high_52w'))}",
        f"  52-Week Low: ${fmt(data.get('low_52w'))}",
        f"  Support: ${fmt(data.get('support'))}",
        f"  Resistance: ${fmt(data.get('resistance'))}",
        "",
        "BOLLINGER BANDS:",
        f"  Upper: ${fmt(data.get('bb_upper'))}",
        f"  Middle: ${fmt(data.get('bb_middle'))}",
        f"  Lower: ${fmt(data.get('bb_lower'))}",
    ]

    return "\n".join(lines)
