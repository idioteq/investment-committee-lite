"""Technical Agent - analyzes price action and entry/exit timing."""

import json
from committee_lite.llm import LLMClient
from committee_lite.schemas import AgentOutput
from committee_lite.tools import get_technical_indicators, format_technical_summary


class TechnicalAgent:
    """Analyzes technical indicators and entry/exit timing."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Technical Agent.

        Args:
            llm_client: LLM client for analysis
        """
        self.llm_client = llm_client
        self.agent_name = "Technical"

    def analyze(self, ticker: str) -> AgentOutput:
        """
        Perform technical analysis.

        Args:
            ticker: Stock ticker to analyze

        Returns:
            AgentOutput with technical analysis
        """
        # Fetch technical indicators
        technical_data = get_technical_indicators(ticker)
        tech_summary = format_technical_summary(technical_data)

        # Build prompt
        system_prompt = """You are a Technical Analyst for an investment committee.

Your job is to assess price momentum, trend, and entry/exit timing.

You MUST respond with valid JSON matching this exact schema:
{
    "score_0_100": <integer from 0-100>,
    "bull_points": [<max 3 bullish arguments as strings>],
    "bear_points": [<max 3 bearish arguments as strings>],
    "key_risks": [<max 3 material risks as strings>],
    "confidence": "<Low|Medium|High>",
    "evidence": [<list of specific data sources and evidence>]
}

Focus on: trend direction, RSI/MACD signals, support/resistance levels, momentum.
Be specific with exact values. Cite your indicators in the evidence field."""

        user_prompt = f"""Analyze the technical setup for {ticker}.

TECHNICAL INDICATORS:
{tech_summary}

Provide your analysis as JSON following the required schema.
Score 0-100 where:
- 80-100: Strong buy signal (oversold, bullish breakout, strong momentum)
- 60-79: Buy signal (positive technicals, good entry)
- 40-59: Neutral (mixed signals, no clear trend)
- 20-39: Sell signal (bearish technicals, distribution)
- 0-19: Strong sell signal (overbought, breakdown, weak momentum)

Consider: Trend, RSI/MACD, support/resistance, volume. Is this a good entry point?"""

        # Get LLM response
        response = self.llm_client.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.7,
        )

        # Parse JSON response (strip markdown code blocks if present)
        try:
            # Remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]  # Remove ```
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
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
