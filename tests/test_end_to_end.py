"""End-to-end integration tests."""

import pytest
from committee_lite.orchestrator import InvestmentCommittee
from committee_lite.llm import get_llm_client


def test_mock_mode_end_to_end():
    """Test full pipeline in mock mode (no API keys needed)."""
    # This should work without any API keys
    client = get_llm_client(mock=True)
    committee = InvestmentCommittee(llm_client=client)

    decision = committee.analyze("NVDA")

    # Verify all components are present
    assert decision.ticker == "NVDA"
    assert decision.final_rating
    assert decision.final_confidence
    assert decision.agent_scores
    assert decision.rationale
    assert decision.action_plan
    assert decision.invalidation_criteria

    # Verify can be serialized
    decision_dict = decision.model_dump()
    assert isinstance(decision_dict, dict)
    assert "ticker" in decision_dict
    assert "final_rating" in decision_dict

    # Verify can be rendered as string
    decision_str = str(decision)
    assert "NVDA" in decision_str
    assert "RATING" in decision_str


def test_multiple_tickers():
    """Test analyzing multiple tickers in sequence."""
    client = get_llm_client(mock=True)
    committee = InvestmentCommittee(llm_client=client)

    tickers = ["AAPL", "MSFT", "GOOGL"]
    decisions = []

    for ticker in tickers:
        decision = committee.analyze(ticker)
        decisions.append(decision)

    # Verify each has correct ticker
    for ticker, decision in zip(tickers, decisions):
        assert decision.ticker == ticker
        assert decision.final_rating


def test_debate_log_structure():
    """Test debate log has correct structure."""
    client = get_llm_client(mock=True)
    committee = InvestmentCommittee(
        llm_client=client,
        disagreement_threshold=5,  # Low threshold to force debate
    )

    decision = committee.analyze("NVDA")

    # If debate occurred, verify structure
    for round in decision.debate_log:
        assert round.round_number > 0
        assert round.trigger
        assert isinstance(round.agent_updates, list)
        assert round.outcome

        # Each update should have required fields
        for update in round.agent_updates:
            assert "agent_name" in update
            assert "old_score" in update
            assert "new_score" in update
            assert "reasoning" in update
