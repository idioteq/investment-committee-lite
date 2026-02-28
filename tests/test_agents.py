"""Test specialist agents."""

import pytest
from committee_lite.agents import (
    FundamentalsAgent,
    ValuationAgent,
    TechnicalAgent,
    SentimentAgent,
)
from committee_lite.llm import get_llm_client
from committee_lite.schemas import AgentOutput


@pytest.fixture
def mock_client():
    """Get mock LLM client."""
    return get_llm_client(mock=True)


def test_fundamentals_agent(mock_client):
    """Test Fundamentals agent returns valid output."""
    agent = FundamentalsAgent(mock_client)
    output = agent.analyze("NVDA")

    assert isinstance(output, AgentOutput)
    assert output.agent_name == "Fundamentals"
    assert output.ticker == "NVDA"
    assert 0 <= output.score_0_100 <= 100
    assert len(output.bull_points) <= 3
    assert len(output.bear_points) <= 3
    assert len(output.key_risks) <= 3
    assert output.confidence in ["Low", "Medium", "High"]
    assert len(output.evidence) > 0


def test_valuation_agent(mock_client):
    """Test Valuation agent returns valid output."""
    agent = ValuationAgent(mock_client)
    output = agent.analyze("AAPL")

    assert isinstance(output, AgentOutput)
    assert output.agent_name == "Valuation"
    assert output.ticker == "AAPL"
    assert 0 <= output.score_0_100 <= 100


def test_technical_agent(mock_client):
    """Test Technical agent returns valid output."""
    agent = TechnicalAgent(mock_client)
    output = agent.analyze("TSLA")

    assert isinstance(output, AgentOutput)
    assert output.agent_name == "Technical"
    assert output.ticker == "TSLA"
    assert 0 <= output.score_0_100 <= 100


def test_sentiment_agent(mock_client):
    """Test Sentiment agent returns valid output."""
    agent = SentimentAgent(mock_client)
    output = agent.analyze("MSFT")

    assert isinstance(output, AgentOutput)
    assert output.agent_name == "Sentiment"
    assert output.ticker == "MSFT"
    assert 0 <= output.score_0_100 <= 100
