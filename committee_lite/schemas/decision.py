"""Schema for final investment decision and debate tracking."""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime


class DissentingView(BaseModel):
    """Captures an agent's disagreement with consensus."""

    agent_name: str = Field(..., description="Name of dissenting agent")
    original_score: int = Field(..., description="Agent's original score")
    final_score: int = Field(..., description="Agent's final score after reconciliation")
    reason: str = Field(..., description="Why this agent disagrees with consensus")


class DebateRound(BaseModel):
    """Tracks a single round of disagreement reconciliation."""

    round_number: int = Field(..., description="Round number (1-indexed)")
    trigger: str = Field(..., description="What triggered this round (e.g., 'score spread 25 > threshold 15')")
    agent_updates: List[dict] = Field(
        ...,
        description="List of agent updates in this round (agent_name, old_score, new_score, reasoning)"
    )
    outcome: str = Field(..., description="Outcome of this round (e.g., 'consensus reached', 'max rounds hit')")


class FinalDecision(BaseModel):
    """Final investment committee decision."""

    ticker: str = Field(..., description="Stock ticker analyzed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    # Agent scores
    agent_scores: dict[str, int] = Field(..., description="Individual agent scores (agent_name -> score)")
    average_score: float = Field(..., description="Average score across all agents")
    score_spread: int = Field(..., description="Max score - Min score")

    # Final rating
    final_rating: Literal[
        "STRONG BUY",
        "BUY",
        "HOLD",
        "SELL",
        "STRONG SELL"
    ] = Field(..., description="Portfolio Manager's final recommendation")

    final_confidence: Literal["Low", "Medium", "High"] = Field(
        ...,
        description="Confidence in final recommendation"
    )

    # Rationale
    rationale: List[str] = Field(
        ...,
        max_length=5,
        description="Top 5 bullets explaining the recommendation"
    )

    # Dissent tracking
    dissenting_views: List[DissentingView] = Field(
        default_factory=list,
        description="Agents that disagree with consensus"
    )

    # Action plan
    action_plan: str = Field(
        ...,
        description="High-level entry approach and monitoring guidance (no specific price targets)"
    )

    invalidation_criteria: List[str] = Field(
        ...,
        max_length=3,
        description="Top 3 conditions that would invalidate the thesis"
    )

    # Debate log
    debate_log: List[DebateRound] = Field(
        default_factory=list,
        description="Full transcript of disagreement reconciliation rounds"
    )

    def __str__(self) -> str:
        """Human-readable decision packet."""
        lines = [
            "",
            "=" * 80,
            f"INVESTMENT COMMITTEE DECISION: {self.ticker}",
            "=" * 80,
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "AGENT SCORES:",
            "-" * 40,
        ]

        for agent_name, score in self.agent_scores.items():
            lines.append(f"  {agent_name:20s}: {score:3d}/100")

        lines.extend([
            "",
            f"Average Score: {self.average_score:.1f}/100",
            f"Score Spread:  {self.score_spread} points",
            "",
            "=" * 80,
            f"FINAL RATING: {self.final_rating}",
            f"CONFIDENCE:   {self.final_confidence}",
            "=" * 80,
            "",
            "RATIONALE:",
        ])

        for i, point in enumerate(self.rationale, 1):
            lines.append(f"  {i}. {point}")

        if self.dissenting_views:
            lines.extend([
                "",
                "DISSENTING VIEWS:",
                "-" * 40,
            ])
            for dissent in self.dissenting_views:
                lines.append(
                    f"  • {dissent.agent_name}: {dissent.original_score}→{dissent.final_score}/100"
                )
                lines.append(f"    Reason: {dissent.reason}")

        lines.extend([
            "",
            "ACTION PLAN:",
            "-" * 40,
            self.action_plan,
            "",
            "INVALIDATION CRITERIA:",
            "-" * 40,
        ])

        for i, criterion in enumerate(self.invalidation_criteria, 1):
            lines.append(f"  {i}. {criterion}")

        # Debate log
        if self.debate_log:
            lines.extend([
                "",
                "=" * 80,
                "DEBATE LOG",
                "=" * 80,
            ])
            for debate_round in self.debate_log:
                lines.extend([
                    "",
                    f"Round {debate_round.round_number}: {debate_round.trigger}",
                    "-" * 40,
                ])
                for update in debate_round.agent_updates:
                    agent = update.get('agent_name', 'Unknown')
                    old = update.get('old_score', 'N/A')
                    new = update.get('new_score', 'N/A')
                    reasoning = update.get('reasoning', 'No reasoning provided')
                    lines.append(f"  {agent}: {old}→{new}/100")
                    lines.append(f"    {reasoning}")
                lines.append(f"  Outcome: {debate_round.outcome}")

        lines.extend([
            "",
            "=" * 80,
            "⚠️  EDUCATIONAL DEMO ONLY - NOT INVESTMENT ADVICE",
            "=" * 80,
            "",
        ])

        return "\n".join(lines)
