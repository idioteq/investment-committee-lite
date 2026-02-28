"""Financial data tool using yfinance."""

import yfinance as yf
from typing import Dict, Any


def get_financial_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch financial data for a ticker using yfinance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary containing financial metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Basic info
        data = {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", 0),
        }

        # Valuation metrics
        data.update({
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
        })

        # Profitability metrics
        data.update({
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
        })

        # Financial health
        data.update({
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "debt_to_equity": info.get("debtToEquity"),
            "total_cash": info.get("totalCash"),
            "total_debt": info.get("totalDebt"),
            "free_cash_flow": info.get("freeCashflow"),
            "operating_cash_flow": info.get("operatingCashflow"),
        })

        # Get financial statements
        try:
            balance_sheet = stock.balance_sheet
            if not balance_sheet.empty:
                # Get most recent column (latest period)
                latest = balance_sheet.columns[0]
                data["total_assets"] = balance_sheet.loc["Total Assets", latest]
                data["total_liabilities"] = balance_sheet.loc["Total Liabilities Net Minority Interest", latest]
        except Exception:
            pass

        try:
            income_stmt = stock.income_stmt
            if not income_stmt.empty:
                latest = income_stmt.columns[0]
                data["revenue"] = income_stmt.loc["Total Revenue", latest]
                data["net_income"] = income_stmt.loc["Net Income", latest]
        except Exception:
            pass

        # Beta for CAPM
        data["beta"] = info.get("beta", 1.0)

        # Analyst recommendations
        data["recommendation"] = info.get("recommendationKey", "hold")
        data["target_price"] = info.get("targetMeanPrice")
        data["num_analyst_opinions"] = info.get("numberOfAnalystOpinions")

        return data

    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e),
            "company_name": ticker,
        }


def format_financial_summary(data: Dict[str, Any]) -> str:
    """
    Format financial data into a readable summary.

    Args:
        data: Dictionary from get_financial_data()

    Returns:
        Formatted string summary
    """
    if "error" in data:
        return f"Error fetching data for {data['ticker']}: {data['error']}"

    def fmt(value, suffix=""):
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            if suffix == "%":
                return f"{value*100:.1f}%"
            elif suffix == "B":
                return f"${value/1e9:.1f}B"
            elif suffix == "M":
                return f"${value/1e6:.0f}M"
            else:
                return f"{value:,.2f}"
        return str(value)

    lines = [
        f"Company: {data.get('company_name', 'N/A')} ({data['ticker']})",
        f"Sector: {data.get('sector', 'N/A')} | Industry: {data.get('industry', 'N/A')}",
        f"Market Cap: {fmt(data.get('market_cap'), 'B')}",
        f"Current Price: ${fmt(data.get('current_price'))}",
        "",
        "VALUATION:",
        f"  P/E: {fmt(data.get('pe_ratio'))} | Forward P/E: {fmt(data.get('forward_pe'))}",
        f"  P/B: {fmt(data.get('price_to_book'))} | P/S: {fmt(data.get('price_to_sales'))}",
        f"  PEG: {fmt(data.get('peg_ratio'))}",
        "",
        "PROFITABILITY:",
        f"  Profit Margin: {fmt(data.get('profit_margin'), '%')} | Operating Margin: {fmt(data.get('operating_margin'), '%')}",
        f"  ROE: {fmt(data.get('roe'), '%')} | ROA: {fmt(data.get('roa'), '%')}",
        f"  Revenue Growth: {fmt(data.get('revenue_growth'), '%')} | Earnings Growth: {fmt(data.get('earnings_growth'), '%')}",
        "",
        "FINANCIAL HEALTH:",
        f"  Current Ratio: {fmt(data.get('current_ratio'))} | Quick Ratio: {fmt(data.get('quick_ratio'))}",
        f"  Debt/Equity: {fmt(data.get('debt_to_equity'))}",
        f"  Free Cash Flow: {fmt(data.get('free_cash_flow'), 'M')}",
        "",
        "ANALYST VIEW:",
        f"  Recommendation: {data.get('recommendation', 'N/A').upper()}",
        f"  Target Price: ${fmt(data.get('target_price'))} ({data.get('num_analyst_opinions', 0)} analysts)",
    ]

    return "\n".join(lines)
