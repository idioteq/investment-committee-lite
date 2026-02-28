"""Valuation Agent - performs 2-stage DCF analysis."""

import json
from committee_lite.llm import LLMClient
from committee_lite.schemas import AgentOutput
from committee_lite.tools import get_financial_data, calculate_dcf_value, format_dcf_summary


class ValuationAgent:
    """Performs intrinsic value analysis using 2-stage DCF."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Valuation Agent.

        Args:
            llm_client: LLM client for analysis
        """
        self.llm_client = llm_client
        self.agent_name = "Valuation"

    def analyze(self, ticker: str) -> AgentOutput:
        """
        Perform DCF valuation analysis.

        Args:
            ticker: Stock ticker to analyze

        Returns:
            AgentOutput with valuation analysis
        """
        # Fetch financial data
        financial_data = get_financial_data(ticker)

        # Calculate DCF
        dcf_results = calculate_dcf_value(ticker, financial_data)
        dcf_summary = format_dcf_summary(dcf_results)

        # Build prompt
        system_prompt = """You are a Valuation Analyst for an investment committee.

Your job is to assess intrinsic value vs. market price using DCF analysis.

You MUST respond with valid JSON matching this exact schema:
{
    "score_0_100": <integer from 0-100>,
    "bull_points": [<max 3 bullish arguments as strings>],
    "bear_points": [<max 3 bearish arguments as strings>],
    "key_risks": [<max 3 material risks as strings>],
    "confidence": "<Low|Medium|High>",
    "evidence": [<list of specific data sources and evidence>]
}

Focus on: margin of safety, DCF assumptions, sensitivity to growth/WACC, valuation multiples.
Be specific with numbers. Cite your calculations in the evidence field."""

        user_prompt = f"""Analyze the valuation of {ticker}.

DCF VALUATION RESULTS:
{dcf_summary}

Provide your analysis as JSON following the required schema.
Score 0-100 where:
- 80-100: Deep value (>50% upside, significant margin of safety)
- 60-79: Undervalued (20-50% upside, good margin of safety)
- 40-59: Fair value (±20% of intrinsic value)
- 20-39: Overvalued (20-50% downside, no margin of safety)
- 0-19: Extremely overvalued (>50% downside, avoid)

Consider: Is upside/downside compelling? How sensitive to assumptions? Terminal value concerns?"""

        # Get LLM response
        response = self.llm_client.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.7,
        )

        # Parse JSON response
        try:
            data = json.loads(response)
            return AgentOutput(
                agent_name=self.agent_name,
                ticker=ticker,
                **data
            )
        except (json.JSONDecodeError, Exception) as e:
            # Fallback
            return AgentOutput(
                agent_name=self.agent_name,
                ticker=ticker,
                score_0_100=50,
                bull_points=["Unable to parse LLM response"],
                bear_points=["JSON parsing error"],
                key_risks=[f"Analysis error: {str(e)}"],
                confidence="Low",
                evidence=["Error in LLM response parsing"]
            )
