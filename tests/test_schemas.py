"""Test Pydantic schemas."""

import pytest
from datetime import datetime
from committee_lite.schemas import AgentOutput, FinalDecision, DebateRound, DissentingView


def test_agent_output_valid():
    """Test valid AgentOutput creation."""
    output = AgentOutput(
        agent_name="Test",
        ticker="AAPL",
        score_0_100=75,
        bull_points=["Point 1", "Point 2"],
        bear_points=["Risk 1"],
        key_risks=["Risk A", "Risk B"],
        confidence="High",
        evidence=["Source 1", "Source 2"]
    )

    assert output.agent_name == "Test"
    assert output.score_0_100 == 75
    assert len(output.bull_points) == 2
    assert output.confidence == "High"


def test_agent_output_score_validation():
    """Test score must be 0-100."""
    with pytest.raises(ValueError):
        AgentOutput(
            agent_name="Test",
            ticker="AAPL",
            score_0_100=150,  # Invalid
            bull_points=["A"],
            bear_points=["B"],
            key_risks=["C"],
            confidence="High",
            evidence=["D"]
        )


def test_agent_output_max_bullets():
    """Test maximum 3 bullets per list."""
    with pytest.raises(ValueError):
        AgentOutput(
            agent_name="Test",
            ticker="AAPL",
            score_0_100=50,
            bull_points=["1", "2", "3", "4"],  # Too many
            bear_points=["A"],
            key_risks=["B"],
            confidence="Medium",
            evidence=["C"]
        )


def test_final_decision_valid():
    """Test valid FinalDecision creation."""
    decision = FinalDecision(
        ticker="NVDA",
        agent_scores={"Fundamentals": 80, "Valuation": 70},
        average_score=75.0,
        score_spread=10,
        final_rating="BUY",
        final_confidence="High",
        rationale=["Reason 1", "Reason 2"],
        action_plan="Buy on dips",
        invalidation_criteria=["Revenue decline"],
    )

    assert decision.ticker == "NVDA"
    assert decision.final_rating == "BUY"
    assert decision.score_spread == 10
    assert len(decision.rationale) == 2


def test_debate_round():
    """Test DebateRound schema."""
    debate = DebateRound(
        round_number=1,
        trigger="spread > threshold",
        agent_updates=[
            {"agent_name": "Fundamentals", "old_score": 70, "new_score": 75, "reasoning": "Adjusted"}
        ],
        outcome="consensus reached"
    )

    assert debate.round_number == 1
    assert len(debate.agent_updates) == 1


def test_dissenting_view():
    """Test DissentingView schema."""
    dissent = DissentingView(
        agent_name="Technical",
        original_score=50,
        final_score=55,
        reason="Still bearish on chart setup"
    )

    assert dissent.agent_name == "Technical"
    assert dissent.final_score == 55
