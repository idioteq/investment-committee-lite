"""Schema for individual agent outputs."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, List


class AgentOutput(BaseModel):
    """Standardized output from a specialist agent."""

    agent_name: str = Field(..., description="Name of the agent (e.g., 'Fundamentals', 'Valuation')")
    ticker: str = Field(..., description="Stock ticker analyzed")
    score_0_100: int = Field(..., ge=0, le=100, description="Investment score from 0 to 100")

    bull_points: List[str] = Field(
        ...,
        max_length=3,
        description="Top 3 bullish arguments"
    )
    bear_points: List[str] = Field(
        ...,
        max_length=3,
        description="Top 3 bearish arguments"
    )
    key_risks: List[str] = Field(
        ...,
        max_length=3,
        description="Top 3 material risks"
    )

    confidence: Literal["Low", "Medium", "High"] = Field(
        ...,
        description="Agent's confidence in this analysis"
    )

    evidence: List[str] = Field(
        ...,
        description="Data sources and specific evidence supporting the analysis"
    )

    @field_validator('bull_points', 'bear_points', 'key_risks')
    @classmethod
    def validate_max_length(cls, v: List[str]) -> List[str]:
        """Ensure lists have at most 3 items."""
        if len(v) > 3:
            raise ValueError("Maximum 3 items allowed")
        return v

    def __str__(self) -> str:
        """Human-readable representation."""
        lines = [
            f"{'='*60}",
            f"{self.agent_name} Agent Analysis: {self.ticker}",
            f"{'='*60}",
            f"Score: {self.score_0_100}/100 | Confidence: {self.confidence}",
            "",
            "BULL CASE:",
        ]
        for i, point in enumerate(self.bull_points, 1):
            lines.append(f"  {i}. {point}")

        lines.append("")
        lines.append("BEAR CASE:")
        for i, point in enumerate(self.bear_points, 1):
            lines.append(f"  {i}. {point}")

        lines.append("")
        lines.append("KEY RISKS:")
        for i, risk in enumerate(self.key_risks, 1):
            lines.append(f"  {i}. {risk}")

        lines.append("")
        lines.append("EVIDENCE:")
        for evidence_item in self.evidence:
            lines.append(f"  • {evidence_item}")

        return "\n".join(lines)
