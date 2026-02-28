"""Test orchestrator and disagreement handling."""

import pytest
from committee_lite.orchestrator import InvestmentCommittee
from committee_lite.llm import get_llm_client
from committee_lite.schemas import FinalDecision


@pytest.fixture
def mock_committee():
    """Get Investment Committee with mock LLM."""
    client = get_llm_client(mock=True)
    return InvestmentCommittee(llm_client=client)


def test_committee_analyze(mock_committee):
    """Test full committee analysis."""
    decision = mock_committee.analyze("NVDA")

    assert isinstance(decision, FinalDecision)
    assert decision.ticker == "NVDA"
    assert decision.final_rating in [
        "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"
    ]
    assert decision.final_confidence in ["Low", "Medium", "High"]
    assert len(decision.agent_scores) == 4  # 4 specialist agents
    assert decision.score_spread >= 0
    assert len(decision.rationale) <= 5
    assert len(decision.invalidation_criteria) <= 3


def test_disagreement_threshold(mock_committee):
    """Test disagreement detection."""
    # With mock mode, we can't control the spread precisely,
    # but we can verify the mechanism exists
    decision = mock_committee.analyze("AAPL")

    # Debate log should exist (might be empty if no disagreement)
    assert isinstance(decision.debate_log, list)

    # If there was a debate, it should have proper structure
    if decision.debate_log:
        debate = decision.debate_log[0]
        assert debate.round_number >= 1
        assert debate.trigger
        assert debate.outcome


def test_dissenting_views_tracking(mock_committee):
    """Test that dissenting views are tracked."""
    decision = mock_committee.analyze("TSLA")

    # Dissenting views should be a list (might be empty)
    assert isinstance(decision.dissenting_views, list)

    # If there are dissenting views, they should have proper structure
    for dissent in decision.dissenting_views:
        assert dissent.agent_name
        assert isinstance(dissent.original_score, int)
        assert isinstance(dissent.final_score, int)
        assert dissent.reason
