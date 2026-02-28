"""Investment Committee orchestration with disagreement handling."""

import json
from typing import List, Dict, Any
from datetime import datetime

from committee_lite.llm import LLMClient, get_llm_client
from committee_lite.agents import (
    FundamentalsAgent,
    ValuationAgent,
    TechnicalAgent,
    SentimentAgent,
)
from committee_lite.orchestrator.portfolio_manager import PortfolioManagerAgent
from committee_lite.schemas import AgentOutput, FinalDecision, DebateRound, DissentingView
from committee_lite.config import Config


class InvestmentCommittee:
    """Orchestrates multi-agent investment analysis with disagreement handling."""

    def __init__(
        self,
        llm_client: LLMClient = None,
        disagreement_threshold: int = None,
        max_reconcile_rounds: int = None,
    ):
        """
        Initialize Investment Committee.

        Args:
            llm_client: LLM client (defaults to configured provider)
            disagreement_threshold: Score spread that triggers reconciliation
            max_reconcile_rounds: Maximum reconciliation rounds
        """
        self.llm_client = llm_client or get_llm_client()
        self.disagreement_threshold = disagreement_threshold or Config.DISAGREEMENT_THRESHOLD
        self.max_reconcile_rounds = max_reconcile_rounds or Config.MAX_RECONCILE_ROUNDS

        # Initialize specialist agents
        self.fundamentals_agent = FundamentalsAgent(self.llm_client)
        self.valuation_agent = ValuationAgent(self.llm_client)
        self.technical_agent = TechnicalAgent(self.llm_client)
        self.sentiment_agent = SentimentAgent(self.llm_client)

        # Initialize portfolio manager
        self.portfolio_manager = PortfolioManagerAgent(self.llm_client)

    def analyze(self, ticker: str) -> FinalDecision:
        """
        Run full investment committee analysis.

        Args:
            ticker: Stock ticker to analyze

        Returns:
            FinalDecision with complete analysis and debate log
        """
        print(f"\n{'='*60}")
        print(f"INVESTMENT COMMITTEE ANALYSIS: {ticker}")
        print(f"{'='*60}\n")

        # Phase 1: Initial agent analyses
        print("Phase 1: Running specialist agent analyses...")
        agent_outputs = self._run_initial_analyses(ticker)

        # Calculate score spread
        scores = [output.score_0_100 for output in agent_outputs]
        score_spread = max(scores) - min(scores)
        average_score = sum(scores) / len(scores)

        print(f"\nInitial scores: {scores}")
        print(f"Average: {average_score:.1f}/100")
        print(f"Spread: {score_spread} points")

        # Phase 2: Disagreement handling
        debate_log = []
        dissenting_views = []

        if score_spread > self.disagreement_threshold:
            print(f"\n⚠️  Score spread ({score_spread}) exceeds threshold ({self.disagreement_threshold})")
            print("Phase 2: Running disagreement reconciliation...")

            agent_outputs, debate_log, dissenting_views = self._handle_disagreement(
                ticker, agent_outputs, score_spread
            )

            # Recalculate after reconciliation
            scores = [output.score_0_100 for output in agent_outputs]
            score_spread = max(scores) - min(scores)
            average_score = sum(scores) / len(scores)

            print(f"\nFinal scores after reconciliation: {scores}")
            print(f"Average: {average_score:.1f}/100")
            print(f"Spread: {score_spread} points")
        else:
            print(f"\n✓ Score spread ({score_spread}) within threshold ({self.disagreement_threshold})")
            print("Proceeding to final synthesis...")

        # Phase 3: Portfolio Manager synthesis
        print("\nPhase 3: Portfolio Manager synthesis...")
        pm_output = self.portfolio_manager.synthesize(
            ticker, agent_outputs, dissenting_views
        )

        # Build final decision
        agent_scores = {output.agent_name: output.score_0_100 for output in agent_outputs}

        final_decision = FinalDecision(
            ticker=ticker,
            timestamp=datetime.now(),
            agent_scores=agent_scores,
            average_score=average_score,
            score_spread=score_spread,
            final_rating=pm_output.get('final_rating', 'HOLD'),
            final_confidence=pm_output.get('final_confidence', 'Low'),
            rationale=pm_output.get('rationale', []),
            dissenting_views=[DissentingView(**d) for d in dissenting_views],
            action_plan=pm_output.get('action_plan', ''),
            invalidation_criteria=pm_output.get('invalidation_criteria', []),
            debate_log=debate_log,
        )

        print("\n✓ Analysis complete!")
        return final_decision

    def _run_initial_analyses(self, ticker: str) -> List[AgentOutput]:
        """Run all specialist agents' initial analyses."""
        agents = [
            ("Fundamentals", self.fundamentals_agent),
            ("Valuation", self.valuation_agent),
            ("Technical", self.technical_agent),
            ("Sentiment", self.sentiment_agent),
        ]

        outputs = []
        for name, agent in agents:
            print(f"  Running {name} Agent...")
            output = agent.analyze(ticker)
            outputs.append(output)
            print(f"    Score: {output.score_0_100}/100 | Confidence: {output.confidence}")

        return outputs

    def _handle_disagreement(
        self, ticker: str, agent_outputs: List[AgentOutput], initial_spread: int
    ) -> tuple[List[AgentOutput], List[DebateRound], List[dict]]:
        """
        Handle disagreement through reconciliation round.

        Args:
            ticker: Stock ticker
            agent_outputs: Initial agent outputs
            initial_spread: Initial score spread

        Returns:
            Tuple of (updated_outputs, debate_log, dissenting_views)
        """
        debate_log = []
        dissenting_views = []

        # Run one reconciliation round
        round_num = 1
        trigger = f"score spread {initial_spread} > threshold {self.disagreement_threshold}"

        print(f"\n  Reconciliation Round {round_num}:")
        print(f"    Trigger: {trigger}")

        agent_updates = []
        updated_outputs = []

        for output in agent_outputs:
            old_score = output.score_0_100

            # Ask agent if they want to update
            update_result = self._request_score_update(ticker, output, agent_outputs)

            if update_result['changed']:
                new_score = update_result['score_update']
                reasoning = update_result['reasoning']

                print(f"    {output.agent_name}: {old_score}→{new_score}/100")
                print(f"      Reason: {reasoning}")

                # Create updated output
                updated_output = AgentOutput(
                    agent_name=output.agent_name,
                    ticker=output.ticker,
                    score_0_100=new_score,
                    bull_points=output.bull_points,
                    bear_points=output.bear_points,
                    key_risks=output.key_risks,
                    confidence=output.confidence,
                    evidence=output.evidence,
                )
                updated_outputs.append(updated_output)

                agent_updates.append({
                    "agent_name": output.agent_name,
                    "old_score": old_score,
                    "new_score": new_score,
                    "reasoning": reasoning
                })

                # Track as dissenting view if still far from average
                new_scores = [o.score_0_100 for o in updated_outputs] + [
                    o.score_0_100 for o in agent_outputs if o not in [output]
                ]
                avg = sum(new_scores) / len(new_scores)

                if abs(new_score - avg) > 10:  # More than 10 points from average
                    dissenting_views.append({
                        "agent_name": output.agent_name,
                        "original_score": old_score,
                        "final_score": new_score,
                        "reason": reasoning
                    })
            else:
                print(f"    {output.agent_name}: {old_score}/100 (no change)")
                updated_outputs.append(output)

        # Record debate round
        outcome = f"Reconciliation complete ({len(agent_updates)} agents updated)"
        debate_round = DebateRound(
            round_number=round_num,
            trigger=trigger,
            agent_updates=agent_updates,
            outcome=outcome
        )
        debate_log.append(debate_round)

        return updated_outputs, debate_log, dissenting_views

    def _request_score_update(
        self, ticker: str, agent_output: AgentOutput, all_outputs: List[AgentOutput]
    ) -> Dict[str, Any]:
        """
        Ask an agent if they want to update their score after seeing others' views.

        Args:
            ticker: Stock ticker
            agent_output: This agent's output
            all_outputs: All agent outputs

        Returns:
            Dict with 'changed' (bool), 'score_update' (int), 'reasoning' (str)
        """
        # Build summary of other agents' views
        other_views = []
        for other in all_outputs:
            if other.agent_name != agent_output.agent_name:
                other_views.append(
                    f"{other.agent_name}: {other.score_0_100}/100 - {other.bull_points[0] if other.bull_points else 'N/A'}"
                )

        other_views_text = "\n".join(other_views)

        system_prompt = f"""You are the {agent_output.agent_name} Agent reviewing your initial score after seeing other agents' perspectives.

Respond with JSON:
{{
    "score_update": <new score 0-100, or same as before if no change>,
    "reasoning": "<why you are or aren't changing your score>"
}}

Only change your score if you genuinely believe another agent's perspective reveals something important you missed.
Most agents should NOT change - only adjust if truly warranted."""

        user_prompt = f"""Your initial analysis for {ticker}:
Score: {agent_output.score_0_100}/100
Bull: {', '.join(agent_output.bull_points)}
Bear: {', '.join(agent_output.bear_points)}

Other agents' views:
{other_views_text}

Do you want to update your score based on this new information?
Respond with JSON containing your score_update and reasoning."""

        response = self.llm_client.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.5,
        )

        try:
            data = json.loads(response)
            new_score = data.get('score_update', agent_output.score_0_100)
            reasoning = data.get('reasoning', 'No reasoning provided')

            changed = new_score != agent_output.score_0_100

            return {
                "changed": changed,
                "score_update": new_score,
                "reasoning": reasoning
            }
        except Exception:
            # If parsing fails, assume no change
            return {
                "changed": False,
                "score_update": agent_output.score_0_100,
                "reasoning": "No update (parsing error)"
            }
