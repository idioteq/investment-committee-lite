"""Mock LLM adapter for testing without API keys."""

from typing import Optional
from committee_lite.llm.client import LLMClient
import json


class MockAdapter(LLMClient):
    """Mock LLM client that returns deterministic canned responses."""

    def __init__(self):
        """Initialize mock adapter."""
        pass

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """Return canned response based on prompt content."""

        # Detect which agent is requesting by checking system_prompt and prompt
        # Check system_prompt first for most specific matches
        sys_prompt = system_prompt or ""

        # Portfolio Manager and reconciliation must be checked first
        # (before individual agents, since PM prompt contains agent names)
        if "Portfolio Manager" in sys_prompt or "synthesize" in sys_prompt.lower():
            return self._portfolio_manager_response(prompt)
        elif "reconcile" in prompt.lower() or "update your score" in prompt.lower():
            return self._reconciliation_response(prompt)
        elif "Fundamental" in sys_prompt:
            return self._fundamentals_response(prompt)
        elif "Valuation" in sys_prompt or "DCF" in sys_prompt:
            return self._valuation_response(prompt)
        elif "Technical" in sys_prompt or "price action" in sys_prompt.lower():
            return self._technical_response(prompt)
        elif "Sentiment" in sys_prompt or "market psychology" in sys_prompt.lower():
            return self._sentiment_response(prompt)
        else:
            return '{"error": "Mock mode: unrecognized agent type"}'

    def _fundamentals_response(self, prompt: str) -> str:
        """Canned fundamentals agent response."""
        return json.dumps({
            "score_0_100": 75,
            "bull_points": [
                "Strong revenue growth at 25% YoY with margin expansion",
                "Fortress balance sheet with $15B cash and minimal debt",
                "Dominant market position with 40% share in core segment"
            ],
            "bear_points": [
                "Premium valuation at 45x P/E vs industry average of 20x",
                "Geographic concentration risk with 60% revenue from single region",
                "Increasing competitive pressure from low-cost entrants"
            ],
            "key_risks": [
                "Regulatory scrutiny in key markets could limit pricing power",
                "Supply chain dependencies on single-source components",
                "Customer concentration with top 5 clients representing 35% revenue"
            ],
            "confidence": "High",
            "evidence": [
                "From yfinance financials: Revenue $50B (+25% YoY), Net Income $8B (+30% YoY)",
                "Balance sheet: Current ratio 2.5, Debt/Equity 0.15",
                "Market data: Market cap $200B, P/E 45x, ROE 22%"
            ]
        }, indent=2)

    def _valuation_response(self, prompt: str) -> str:
        """Canned valuation agent response."""
        return json.dumps({
            "score_0_100": 68,
            "bull_points": [
                "DCF intrinsic value of $185/share vs current $160 implies 15% upside",
                "Conservative WACC of 9% builds in margin of safety",
                "Terminal growth of 3% is below historical 5-year average"
            ],
            "bear_points": [
                "Valuation highly sensitive to terminal growth assumptions",
                "Current P/E of 45x assumes sustained high growth for 5+ years",
                "Limited margin of safety if growth disappoints"
            ],
            "key_risks": [
                "Growth deceleration would compress multiples significantly",
                "Rising interest rates increase WACC and reduce present value",
                "Execution risk on maintaining 20%+ margins at scale"
            ],
            "confidence": "Medium",
            "evidence": [
                "DCF calculation: Stage 1 FCF PV $80/share, Stage 2 Terminal PV $105/share",
                "WACC: 9% (Rf 4.5% + Beta 1.2 * ERP 5% - debt cost benefit)",
                "Assumptions: Revenue growth 20%→15%→10%→3%, FCF margin 18%→20%"
            ]
        }, indent=2)

    def _technical_response(self, prompt: str) -> str:
        """Canned technical agent response."""
        return json.dumps({
            "score_0_100": 72,
            "bull_points": [
                "Price above all major moving averages (20/50/200 SMA)",
                "RSI at 58 indicates room to run before overbought",
                "MACD bullish crossover confirmed with rising histogram"
            ],
            "bear_points": [
                "Extended 40% rally from October lows suggests consolidation risk",
                "Resistance at $165 tested 3 times without breakout",
                "Volume declining on recent advances suggests weakening momentum"
            ],
            "key_risks": [
                "Broader market correction would likely pull stock down 15-20%",
                "Failure at $165 resistance could trigger technical selling to $150",
                "Volatility spike could shake out weak hands despite fundamentals"
            ],
            "confidence": "Medium",
            "evidence": [
                "Price: $160, 20-SMA: $155, 50-SMA: $148, 200-SMA: $135",
                "RSI (14-day): 58, MACD: +2.5 (bullish), Volume: 15M (avg: 18M)",
                "Support: $150/$145, Resistance: $165/$170"
            ]
        }, indent=2)

    def _sentiment_response(self, prompt: str) -> str:
        """Canned sentiment agent response."""
        return json.dumps({
            "score_0_100": 70,
            "bull_points": [
                "Analyst upgrades outnumber downgrades 8:2 in past 30 days",
                "Institutional ownership increased 3% QoQ showing conviction",
                "Social sentiment positive with 65% bullish mentions on major forums"
            ],
            "bear_points": [
                "Retail positioning near extreme bullishness at 85th percentile",
                "Short interest only 2% of float leaves no squeeze potential",
                "Options market pricing in muted 15% annual volatility"
            ],
            "key_risks": [
                "Crowded trade vulnerable to sentiment shift on any negative catalyst",
                "High expectations mean earnings beat must be significant to satisfy",
                "Momentum-driven buying could reverse quickly in risk-off environment"
            ],
            "confidence": "Medium",
            "evidence": [
                "News flow: 45 articles past week, 70% positive, 20% neutral, 10% negative",
                "Analyst consensus: 18 Buy, 8 Hold, 2 Sell, avg target $175 (+9%)",
                "Positioning: Institutional ownership 75%, Short interest 2%, Put/Call ratio 0.65"
            ]
        }, indent=2)

    def _portfolio_manager_response(self, prompt: str) -> str:
        """Canned portfolio manager response."""
        return json.dumps({
            "final_rating": "BUY",
            "final_confidence": "Medium",
            "rationale": [
                "Strong fundamentals (75/100) supported by 25% revenue growth and healthy margins",
                "Valuation (68/100) offers reasonable 15% upside with conservative DCF assumptions",
                "Technical setup (72/100) confirms bullish trend though extended short-term",
                "Positive sentiment (70/100) provides near-term tailwind but limits contrarian edge",
                "Tight score spread (7 points) indicates strong consensus across perspectives"
            ],
            "action_plan": "Consider initiating position in tranches to average in over 2-3 weeks. Monitor for pullback to $150-155 range (near 50-day MA) for better entry. Track earnings beat/miss and guidance as key catalyst. Size position conservatively at 2-3% of portfolio given extended valuation multiples. Use $145 as technical stop (below 200-SMA and prior support).",
            "invalidation_criteria": [
                "Revenue growth decelerates below 15% for two consecutive quarters",
                "Loss of market share to competitors or pricing pressure evident in margins",
                "Technical breakdown below $145 on elevated volume"
            ]
        }, indent=2)

    def _reconciliation_response(self, prompt: str) -> str:
        """Canned reconciliation response."""
        # Most agents would say "no change" in a tight spread scenario
        if "Fundamentals" in prompt:
            return json.dumps({
                "score_update": 75,
                "reasoning": "No change. My fundamental analysis remains unchanged based on the data."
            })
        elif "Valuation" in prompt:
            return json.dumps({
                "score_update": 70,  # Small adjustment
                "reasoning": "Adjusting up 2 points after considering technical's bullish setup adds near-term momentum support to DCF-based target."
            })
        else:
            return json.dumps({
                "score_update": "no change",
                "reasoning": "My assessment stands based on available evidence."
            })
