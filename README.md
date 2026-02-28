# Investment Committee Lite

**A multi-agent investment analysis demo using LLMs.**

> ⚠️ **EDUCATIONAL DEMO ONLY - NOT INVESTMENT ADVICE**
> This is a simplified demonstration of multi-agent systems for investment analysis.
> Not suitable for real investment decisions. For production systems and firm-specific customization, contact the author.

---

## What This Is

A lightweight demo showcasing how multiple AI agents can collaborate to analyze stocks:

- **4 Specialist Agents**: Fundamentals, Valuation (2-stage DCF), Technical, Sentiment
- **1 Portfolio Manager**: Synthesizes specialist views into final decision
- **Disagreement Handling**: Score spread triggers reconciliation round with debate log
- **Structured Output**: Valid JSON schemas enforced via Pydantic
- **Mock Mode**: Runs without API keys using canned responses
- **Provider Agnostic**: Supports OpenAI and Anthropic

## What This Isn't

- ❌ Not a production trading system
- ❌ Not financial advice
- ❌ Not a backtesting framework
- ❌ Not suitable for managing real money

**For production-grade systems with QA harnesses, compliance tracking, and firm-specific customization, contact the author.**

---

## Architecture

![Architecture Diagram](docs/images/architecture.png)

**System Flow:**
1. **4 Specialist Agents** analyze the stock independently (Fundamentals, Valuation, Technical, Sentiment)
2. **Score Spread Check** determines if agent scores diverge beyond threshold
3. **Reconciliation Round** (optional) allows agents to update scores after reviewing peers' perspectives
4. **Portfolio Manager** synthesizes all views into final decision
5. **Output** includes decision packet, dissent log, and structured JSON

---

## Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/yourusername/investment-committee-lite.git
cd investment-committee-lite

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Run in Mock Mode (No API Keys Needed)

```bash
# Analyze NVIDIA using canned responses
uv run committee-lite analyze NVDA --mock
```

### Run with Real LLMs

1. Copy environment template:
```bash
cp .env.example .env
```

2. Add your API key to `.env`:
```bash
# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Or for Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

3. Run analysis:
```bash
# With OpenAI
uv run committee-lite analyze AAPL

# With Anthropic
uv run committee-lite analyze TSLA --provider anthropic

# Save JSON output
uv run committee-lite analyze MSFT --json
```

---

## Example Output

```
================================================================================
INVESTMENT COMMITTEE DECISION: NVDA
================================================================================
Timestamp: 2026-02-27 14:30:00

AGENT SCORES:
----------------------------------------
  Fundamentals        :  75/100
  Valuation           :  68/100
  Technical           :  72/100
  Sentiment           :  70/100

Average Score: 71.2/100
Score Spread:  7 points

================================================================================
FINAL RATING: BUY
CONFIDENCE:   Medium
================================================================================

RATIONALE:
  1. Strong fundamentals (75/100) supported by 25% revenue growth and healthy margins
  2. Valuation (68/100) offers reasonable 15% upside with conservative DCF assumptions
  3. Technical setup (72/100) confirms bullish trend though extended short-term
  4. Positive sentiment (70/100) provides near-term tailwind but limits contrarian edge
  5. Tight score spread (7 points) indicates strong consensus across perspectives

ACTION PLAN:
----------------------------------------
Consider initiating position in tranches to average in over 2-3 weeks. Monitor for
pullback to better entry levels. Track earnings beat/miss and guidance as key catalyst.
Size position conservatively given extended valuation multiples.

INVALIDATION CRITERIA:
----------------------------------------
  1. Revenue growth decelerates below 15% for two consecutive quarters
  2. Loss of market share to competitors or pricing pressure evident in margins
  3. Technical breakdown below key support levels on elevated volume

================================================================================
⚠️  EDUCATIONAL DEMO ONLY - NOT INVESTMENT ADVICE
================================================================================
```

See `examples/` directory for complete JSON output and debate logs.

---

## Features

### 1. Specialist Agents

Each agent has a focused mandate:

**Fundamentals Agent**
- Analyzes business quality, financial health, competitive moat
- Metrics: ROE, margins, balance sheet strength, revenue quality
- Scores 0-100: 80-100 (exceptional), 60-79 (high quality), 40-59 (average), <40 (below average)

**Valuation Agent**
- Calculates intrinsic value using 2-stage DCF
- Stage 1: Years 1-5 explicit forecast
- Stage 2: Terminal value (Gordon Growth)
- Scores based on upside/downside vs market price

**Technical Agent**
- Analyzes price action, momentum, entry/exit timing
- Indicators: RSI, MACD, moving averages, support/resistance
- Scores based on technical setup quality

**Sentiment Agent**
- Assesses market psychology, analyst consensus, positioning
- Limited data in demo (analyst recommendations only)
- Scores based on bullish/bearish positioning

### 2. Disagreement Handling

When agent score spread exceeds threshold (default: 15 points):
1. Triggers reconciliation round
2. Each agent reviews others' perspectives
3. Can update their score with reasoning
4. All updates logged in debate transcript
5. Dissenting views explicitly documented

![Disagreement Handling Flow](docs/images/disagreement-handling.png)

### 3. Structured Output

All outputs are Pydantic models:
- Type-safe, validated JSON
- Max 3 bullets per list (bull/bear/risks)
- Evidence citations required
- Confidence levels (Low/Medium/High)

### 4. Mock Mode

Perfect for testing, CI/CD, and demonstrations:
- No API keys required
- Deterministic canned responses
- Full pipeline exercised
- Tests can run anywhere

![Mock Mode vs Real Mode](docs/images/mock-mode.png)

---

## CLI Reference

```bash
# Basic usage
committee-lite analyze <TICKER>

# Options
  --mock                Use mock mode (no API keys)
  --provider <name>     LLM provider (openai|anthropic)
  --model <name>        Model name (default: from .env)
  --threshold <n>       Disagreement threshold (default: 15)
  --max-rounds <n>      Max reconciliation rounds (default: 1)
  --json                Save JSON output to outputs/
  --max-tokens <n>      Max tokens per LLM call (default: 2000)
  --temperature <f>     LLM temperature (default: 0.7)

# Examples
committee-lite analyze NVDA --mock
committee-lite analyze AAPL --provider openai --json
committee-lite analyze TSLA --threshold 20 --max-rounds 2
```

---

## Development

### Run Tests

```bash
# All tests (uses mock mode - no API keys needed)
uv run pytest

# With coverage
uv run pytest --cov=committee_lite

# Specific test file
uv run pytest tests/test_schemas.py
```

### Project Structure

```
investment-committee-lite/
├── committee_lite/          # Main package
│   ├── agents/              # Specialist agents
│   │   ├── fundamentals.py
│   │   ├── valuation.py
│   │   ├── technical.py
│   │   └── sentiment.py
│   ├── orchestrator/        # Committee orchestration
│   │   ├── committee.py     # InvestmentCommittee class
│   │   └── portfolio_manager.py
│   ├── tools/               # Data tools
│   │   ├── financial_data.py
│   │   ├── technical_indicators.py
│   │   └── dcf_calculator.py
│   ├── llm/                 # LLM client abstraction
│   │   ├── client.py
│   │   ├── openai_adapter.py
│   │   ├── anthropic_adapter.py
│   │   └── mock_adapter.py
│   ├── schemas/             # Pydantic models
│   │   ├── agent_output.py
│   │   └── decision.py
│   ├── config.py            # Configuration
│   └── cli.py               # CLI interface
├── tests/                   # Test suite
├── examples/                # Sample outputs
├── outputs/                 # Generated outputs (gitignored)
└── README.md
```

---

## Extending the System

### Add a New Agent

1. Create agent class in `committee_lite/agents/`:

```python
from committee_lite.llm import LLMClient
from committee_lite.schemas import AgentOutput

class MacroAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.agent_name = "Macro"

    def analyze(self, ticker: str) -> AgentOutput:
        # 1. Fetch macro data
        # 2. Build prompt
        # 3. Call LLM
        # 4. Parse to AgentOutput
        pass
```

2. Register in `committee.py`:

```python
self.macro_agent = MacroAgent(self.llm_client)
# Add to _run_initial_analyses()
```

3. Update mock adapter with canned response

4. Add tests

### Add a New Tool

1. Create tool function in `committee_lite/tools/`:

```python
def get_macro_data(ticker: str) -> Dict[str, Any]:
    """Fetch macro economic indicators."""
    try:
        # Fetch data
        return {"ticker": ticker, ...}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}
```

2. Import in `tools/__init__.py`

3. Use in relevant agent

4. Add tests

### Swap LLM Provider

Already supported - just change `.env`:

```bash
# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Use Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

Or via CLI:
```bash
committee-lite analyze AAPL --provider anthropic
```

---

## Limitations & Disclaimers

### Known Limitations

1. **Simplified DCF**: 2-stage model with basic assumptions. Not suitable for complex businesses.
2. **Limited data**: Uses yfinance (free, unofficial). No proprietary data sources.
3. **No backtesting**: No historical performance validation.
4. **No position sizing**: Action plans are qualitative, not quantitative.
5. **No risk management**: No stop-losses, no portfolio construction, no correlation analysis.
6. **Sentiment data**: Limited to analyst consensus (no news scraping, no social sentiment).

### Important Disclaimers

> ⚠️ **NOT INVESTMENT ADVICE**
> This software is provided for educational purposes only. It is not financial advice, investment advice, trading advice, or any other sort of advice. Do not make investment decisions based on this demo.

> ⚠️ **NO WARRANTY**
> This software is provided "as is" without warranty of any kind. Use at your own risk.

> ⚠️ **NOT PRODUCTION-READY**
> This is a demonstration. For production systems with proper QA, compliance, and institutional-grade infrastructure, contact the author for consulting.

---

## FAQ

**Q: Can I use this for real trading?**
A: No. This is an educational demo with simplified assumptions and no backtesting.

**Q: Why not use <Framework X>?**
A: This is intentionally simple for educational purposes. Production systems may benefit from CrewAI, LangGraph, or custom frameworks.

**Q: How accurate is the valuation?**
A: The DCF is simplified for demonstration. Real valuations require sector-specific models, detailed assumptions, and sensitivity analysis.

**Q: Can I add more agents?**
A: Yes! See "Extending the System" above. Keep it simple and educational.

**Q: Does this work without API keys?**
A: Yes! Use `--mock` flag. Perfect for testing and demonstrations.

**Q: What about compliance/audit trails?**
A: This demo has basic debate logs. Production systems need comprehensive audit trails, model governance, and compliance frameworks. Contact author for consulting.

---

## Production Version

**For institutional deployment with:**
- Comprehensive backtesting and validation
- Multi-stock portfolio construction
- Risk parity and correlation analysis
- Compliance tracking and audit trails
- Firm-specific customization
- Integration with existing systems
- QA harnesses and model governance

**Contact:** Jeremy Leung - <your-email-or-linkedin>

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Acknowledgments

- Inspired by the AlphaAgents research paper (arXiv:2508.11152)
- Built with Python, Pydantic, yfinance, OpenAI SDK, Anthropic SDK
- Designed for educational demonstration of multi-agent systems

---

**Remember: This is a demo. Not investment advice. Not for managing real money.**
