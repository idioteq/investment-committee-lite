"""Sentiment Agent - analyzes market psychology and positioning."""

import json
from committee_lite.llm import LLMClient
from committee_lite.schemas import AgentOutput
from committee_lite.tools import get_financial_data


class SentimentAgent:
    """Analyzes market sentiment, analyst views, and positioning."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Sentiment Agent.

        Args:
            llm_client: LLM client for analysis
        """
        self.llm_client = llm_client
        self.agent_name = "Sentiment"

    def analyze(self, ticker: str) -> AgentOutput:
        """
        Perform sentiment analysis.

        Args:
            ticker: Stock ticker to analyze

        Returns:
            AgentOutput with sentiment analysis
        """
        # Fetch financial data (includes analyst recommendations)
        financial_data = get_financial_data(ticker)

        # Extract sentiment-relevant data
        recommendation = financial_data.get('recommendation', 'hold')
        num_analysts = financial_data.get('num_analyst_opinions', 0)
        target_price = financial_data.get('target_price', 0)
        current_price = financial_data.get('current_price', 0)

        analyst_upside = 0
        if current_price and target_price:
            analyst_upside = ((target_price - current_price) / current_price) * 100

        # Build prompt
        system_prompt = """You are a Sentiment Analyst for an investment committee.

Your job is to assess market psychology, analyst views, and positioning.

You MUST respond with valid JSON matching this exact schema:
{
    "score_0_100": <integer from 0-100>,
    "bull_points": [<max 3 bullish arguments as strings>],
    "bear_points": [<max 3 bearish arguments as strings>],
    "key_risks": [<max 3 material risks as strings>],
    "confidence": "<Low|Medium|High>",
    "evidence": [<list of specific data sources and evidence>]
}

Focus on: analyst consensus, crowding, contrarian signals, expectations.
Be specific. Cite your data in the evidence field."""

        user_prompt = f"""Analyze market sentiment for {ticker}.

SENTIMENT DATA:
- Analyst Consensus: {recommendation.upper()} ({num_analysts} analysts)
- Target Price: ${target_price:.2f} (implied {analyst_upside:+.1f}% from ${current_price:.2f})
- Company: {financial_data.get('company_name', ticker)}
- Sector: {financial_data.get('sector', 'N/A')}

Provide your analysis as JSON following the required schema.
Score 0-100 where:
- 80-100: Very bullish sentiment (positive catalysts, upgrades)
- 60-79: Bullish sentiment (favorable positioning)
- 40-59: Neutral sentiment (mixed signals)
- 20-39: Bearish sentiment (negative positioning, downgrades)
- 0-19: Very bearish sentiment (capitulation, extreme pessimism)

Consider: Is the Street bullish or bearish? Crowded trade? Contrarian opportunity?
Note: Limited data available in demo - infer what you can from analyst consensus."""

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
