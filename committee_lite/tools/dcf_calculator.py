"""Simplified 2-Stage DCF Calculator.

This is an educational demo implementing a basic 2-stage DCF:
- Stage 1: Explicit forecast years 1-5
- Stage 2: Terminal value using Gordon Growth Model

NOT FOR REAL INVESTMENT DECISIONS - For demonstration purposes only.
"""

import numpy as np
from typing import Dict, Any, Tuple
import yfinance as yf


# Constants
RISK_FREE_RATE = 0.045  # 4.5% (10Y Treasury)
EQUITY_RISK_PREMIUM = 0.05  # 5.0% standard US ERP
TAX_RATE = 0.21  # 21% corporate tax rate


def fetch_current_treasury_rate() -> float:
    """Fetch current 10Y Treasury rate, fallback to constant."""
    try:
        treasury = yf.Ticker("^TNX")
        hist = treasury.history(period="5d")
        if not hist.empty:
            rate = hist['Close'].iloc[-1] / 100
            return rate
    except Exception:
        pass
    return RISK_FREE_RATE


def calculate_dcf_value(
    ticker: str,
    financial_data: Dict[str, Any],
    growth_rate_stage1: float = 0.15,
    terminal_growth_rate: float = 0.03,
    fcf_margin: float = 0.15,
) -> Dict[str, Any]:
    """
    Calculate 2-stage DCF intrinsic value.

    Args:
        ticker: Stock ticker
        financial_data: Dict from get_financial_data()
        growth_rate_stage1: Revenue growth rate for years 1-5 (default 15%)
        terminal_growth_rate: Perpetual growth rate (default 3%)
        fcf_margin: Free cash flow margin (default 15%)

    Returns:
        Dictionary with DCF results
    """
    try:
        # Extract key metrics
        revenue = financial_data.get('revenue', 0)
        beta = financial_data.get('beta', 1.0)
        market_cap = financial_data.get('market_cap', 0)
        total_debt = financial_data.get('total_debt', 0)
        total_cash = financial_data.get('total_cash', 0)

        if not revenue or not market_cap:
            return {
                "ticker": ticker,
                "error": "Insufficient financial data for DCF calculation"
            }

        # Calculate WACC
        wacc = calculate_wacc(beta, market_cap, total_debt)

        # Project free cash flows
        fcf_projections = []
        current_revenue = revenue

        # Stage 1: Years 1-5 (High Growth)
        for year in range(1, 6):
            current_revenue *= (1 + growth_rate_stage1)
            fcf = current_revenue * fcf_margin
            pv_fcf = fcf / ((1 + wacc) ** year)
            fcf_projections.append({
                "year": year,
                "revenue": current_revenue,
                "fcf": fcf,
                "pv_fcf": pv_fcf
            })

        # Sum of PV(FCF) for years 1-5
        stage1_value = sum(p['pv_fcf'] for p in fcf_projections)

        # Stage 2: Terminal Value (Gordon Growth)
        year5_revenue = fcf_projections[-1]['revenue']
        terminal_fcf = year5_revenue * (1 + terminal_growth_rate) * fcf_margin
        terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
        pv_terminal_value = terminal_value / ((1 + wacc) ** 5)

        # Enterprise Value
        enterprise_value = stage1_value + pv_terminal_value

        # Equity Value
        net_debt = (total_debt or 0) - (total_cash or 0)
        equity_value = enterprise_value - net_debt

        # Shares outstanding (estimate from market cap and current price)
        current_price = financial_data.get('current_price', 0)
        if current_price > 0:
            shares_outstanding = market_cap / current_price
        else:
            shares_outstanding = 0

        # Intrinsic value per share
        intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0

        # Upside/downside
        upside_pct = ((intrinsic_value_per_share - current_price) / current_price * 100) if current_price > 0 else 0

        # Contribution breakdown
        stage1_pct = (stage1_value / enterprise_value * 100) if enterprise_value > 0 else 0
        terminal_pct = (pv_terminal_value / enterprise_value * 100) if enterprise_value > 0 else 0

        return {
            "ticker": ticker,
            "intrinsic_value_per_share": intrinsic_value_per_share,
            "current_price": current_price,
            "upside_downside_pct": upside_pct,
            "wacc": wacc,
            "growth_rate_stage1": growth_rate_stage1,
            "terminal_growth_rate": terminal_growth_rate,
            "fcf_margin": fcf_margin,
            "enterprise_value": enterprise_value,
            "stage1_value": stage1_value,
            "terminal_value_pv": pv_terminal_value,
            "stage1_contribution_pct": stage1_pct,
            "terminal_contribution_pct": terminal_pct,
            "fcf_projections": fcf_projections,
            "assumptions": {
                "Revenue (base)": f"${revenue/1e9:.1f}B",
                "Growth (years 1-5)": f"{growth_rate_stage1*100:.0f}%",
                "Terminal Growth": f"{terminal_growth_rate*100:.1f}%",
                "FCF Margin": f"{fcf_margin*100:.0f}%",
                "WACC": f"{wacc*100:.1f}%",
                "Beta": f"{beta:.2f}",
            }
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "error": f"DCF calculation error: {str(e)}"
        }


def calculate_wacc(beta: float, market_cap: float, total_debt: float, risk_free_rate: float = None) -> float:
    """
    Calculate Weighted Average Cost of Capital.

    WACC = (E/V) * Re + (D/V) * Rd * (1 - Tax)
    where Re = Rf + Beta * ERP
    """
    if risk_free_rate is None:
        risk_free_rate = fetch_current_treasury_rate()

    # Cost of equity (CAPM)
    cost_of_equity = risk_free_rate + (beta * EQUITY_RISK_PREMIUM)

    # Cost of debt (simplified: risk-free + credit spread)
    cost_of_debt = risk_free_rate + 0.02  # 2% credit spread

    # Market value weights
    total_value = market_cap + total_debt
    if total_value == 0:
        return cost_of_equity  # Fallback to all-equity WACC

    equity_weight = market_cap / total_value
    debt_weight = total_debt / total_value

    # WACC
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - TAX_RATE))

    return wacc


def format_dcf_summary(dcf_results: Dict[str, Any]) -> str:
    """Format DCF results into readable summary."""
    if "error" in dcf_results:
        return f"DCF Error for {dcf_results['ticker']}: {dcf_results['error']}"

    def fmt(value, prefix="$", suffix=""):
        if value is None or np.isnan(value):
            return "N/A"
        return f"{prefix}{value:.2f}{suffix}"

    intrinsic = dcf_results.get('intrinsic_value_per_share', 0)
    current = dcf_results.get('current_price', 0)
    upside = dcf_results.get('upside_downside_pct', 0)

    lines = [
        f"2-Stage DCF Valuation: {dcf_results['ticker']}",
        "=" * 50,
        "",
        "VALUATION RESULT:",
        f"  Intrinsic Value: {fmt(intrinsic)} per share",
        f"  Current Price:   {fmt(current)} per share",
        f"  Upside/Downside: {upside:+.1f}%",
        "",
        "ASSUMPTIONS:",
    ]

    for key, value in dcf_results.get('assumptions', {}).items():
        lines.append(f"  {key:20s}: {value}")

    lines.extend([
        "",
        "VALUE CONTRIBUTION:",
        f"  Stage 1 (Years 1-5): {dcf_results.get('stage1_contribution_pct', 0):.1f}%",
        f"  Terminal Value:      {dcf_results.get('terminal_contribution_pct', 0):.1f}%",
        "",
        "⚠️  EDUCATIONAL DEMO - Simplified assumptions",
        "⚠️  NOT FOR REAL INVESTMENT DECISIONS",
    ])

    return "\n".join(lines)
