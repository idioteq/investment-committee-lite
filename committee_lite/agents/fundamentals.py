"""Fundamentals Agent - analyzes business quality and financial health."""

import json
from committee_lite.llm import LLMClient
from committee_lite.schemas import AgentOutput
from committee_lite.tools import get_financial_data, format_financial_summary


class FundamentalsAgent:
    """Analyzes fundamental business quality and financial health."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Fundamentals Agent.

        Args:
            llm_client: LLM client for analysis
        """
        self.llm_client = llm_client
        self.agent_name = "Fundamentals"

    def analyze(self, ticker: str) -> AgentOutput:
        """
        Perform fundamental quality analysis.

        Args:
            ticker: Stock ticker to analyze

        Returns:
            AgentOutput with fundamental analysis
        """
        # Fetch financial data
        financial_data = get_financial_data(ticker)
        data_summary = format_financial_summary(financial_data)

        # Build prompt
        system_prompt = """You are a Fundamental Quality Analyst for an investment committee.

Your job is to assess business quality, financial health, and competitive positioning.

You MUST respond with valid JSON matching this exact schema:
{
    "score_0_100": <integer from 0-100>,
    "bull_points": [<max 3 bullish arguments as strings>],
    "bear_points": [<max 3 bearish arguments as strings>],
    "key_risks": [<max 3 material risks as strings>],
    "confidence": "<Low|Medium|High>",
    "evidence": [<list of specific data sources and evidence>]
}

Focus on: ROE, margins, balance sheet strength, revenue quality, competitive moat.
Be specific with numbers. Cite your data sources in the evidence field."""

        user_prompt = f"""Analyze the fundamental quality of {ticker}.

FINANCIAL DATA:
{data_summary}

Provide your analysis as JSON following the required schema.
Score 0-100 where:
- 80-100: Exceptional quality (wide moat, fortress balance sheet)
- 60-79: High quality (strong position, sustainable advantages)
- 40-59: Average quality (no clear competitive advantage)
- 20-39: Below average (structural challenges)
- 0-19: Poor quality (deteriorating business)

Be concise but specific. Include exact numbers in your points."""

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
            # Fallback if LLM doesn't return valid JSON
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
