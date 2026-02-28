"""Portfolio Manager Agent - synthesizes committee outputs into final decision."""

import json
from typing import List
from committee_lite.llm import LLMClient
from committee_lite.schemas import AgentOutput


class PortfolioManagerAgent:
    """Portfolio Manager that synthesizes specialist agent outputs."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Portfolio Manager.

        Args:
            llm_client: LLM client for synthesis
        """
        self.llm_client = llm_client

    def synthesize(
        self,
        ticker: str,
        agent_outputs: List[AgentOutput],
        dissenting_views: List[dict] = None
    ) -> dict:
        """
        Synthesize final decision from agent outputs.

        Args:
            ticker: Stock ticker
            agent_outputs: List of AgentOutput from specialists
            dissenting_views: Optional list of dissenting agents

        Returns:
            Dictionary with final decision components
        """
        # Prepare agent summaries
        agent_summaries = []
        for output in agent_outputs:
            summary = f"""
{output.agent_name} Agent: {output.score_0_100}/100 (Confidence: {output.confidence})
Bull Points: {', '.join(output.bull_points)}
Bear Points: {', '.join(output.bear_points)}
Key Risks: {', '.join(output.key_risks)}
"""
            agent_summaries.append(summary.strip())

        all_summaries = "\n\n".join(agent_summaries)

        # Build dissent summary if any
        dissent_summary = ""
        if dissenting_views:
            dissent_summary = "\n\nDISSENTING VIEWS:\n"
            for dissent in dissenting_views:
                dissent_summary += f"- {dissent['agent_name']}: {dissent['reason']}\n"

        # Build prompt
        system_prompt = """You are the Portfolio Manager for an investment committee.

Your job is to synthesize specialist agent analyses into a final investment decision.

You MUST respond with valid JSON matching this exact schema:
{
    "final_rating": "<STRONG BUY|BUY|HOLD|SELL|STRONG SELL>",
    "final_confidence": "<Low|Medium|High>",
    "rationale": [<max 5 bullet points explaining the recommendation>],
    "action_plan": "<high-level entry approach and monitoring guidance (no specific prices)>",
    "invalidation_criteria": [<max 3 conditions that would break the thesis>]
}

Integrate all perspectives. Acknowledge dissenting views if any.
Be concise but specific. Focus on actionable insights."""

        user_prompt = f"""Synthesize final investment decision for {ticker}.

AGENT ANALYSES:
{all_summaries}
{dissent_summary}

Provide your synthesis as JSON following the required schema.

Rating guidance:
- STRONG BUY: Compelling opportunity, multiple positive factors, low risk
- BUY: Attractive opportunity, balance tilts positive
- HOLD: Neutral, no clear edge, wait for better setup
- SELL: Unfavorable, balance tilts negative
- STRONG SELL: Avoid, multiple red flags, high risk

Consider: Where do agents agree? Where do they disagree? What's the balance of evidence?
Action plan should be high-level (no specific price targets in demo mode).
Invalidation criteria should be specific conditions (not vague)."""

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
            return data
        except (json.JSONDecodeError, Exception) as e:
            # Fallback
            return {
                "final_rating": "HOLD",
                "final_confidence": "Low",
                "rationale": [
                    "Unable to parse Portfolio Manager response",
                    f"Error: {str(e)}"
                ],
                "action_plan": "Analysis error - review agent outputs manually",
                "invalidation_criteria": ["N/A"]
            }
