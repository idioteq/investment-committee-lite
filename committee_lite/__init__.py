"""Investment Committee Lite - Educational multi-agent investment analysis demo."""

__version__ = "0.1.0"

from committee_lite.orchestrator import InvestmentCommittee
from committee_lite.schemas import AgentOutput, FinalDecision

__all__ = ["InvestmentCommittee", "AgentOutput", "FinalDecision"]
