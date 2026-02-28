# Examples

This directory contains real investment analysis outputs demonstrating the evolution of the multi-agent committee system from December 2025 to February 2026.

---

## Evolution of the System

These examples show the progression from initial prototype to production-grade system:

### Version 1: Alpha-Agents (AutoGen) - January 2026

Initial proof-of-concept using Microsoft AutoGen framework with 5 agents including CatalystAgent.

**Files:**
- `analysis_AAPL_20260122_101319_with_debate.json` - Apple analysis with full debate log
- `analysis_NVDA_20260122_102007_with_debate.json` - NVIDIA analysis with disagreement reconciliation
- `summary of debate on NVidia.md` - Detailed narrative of agent disagreements and resolution

**Key Features:**
- 5 specialist agents (Quality, Value, Technical, Sentiment, Catalyst)
- AutoGen orchestration
- Extensive debate logs showing agent-to-agent dialogue
- JSON output with complete conversation history

**Example Insight from NVDA Debate:**
The Valuation Agent initially scored 5/100 (extremely bearish on valuation), while Quality Agent scored 92/100. After reconciliation, Valuation adjusted to 20/100 after acknowledging operational efficiency metrics. Demonstrates real multi-agent disagreement resolution.

---

### Version 2: CrewAI Migration - Late January 2026

Migrated to CrewAI framework for better cost efficiency and agent coordination.

**Files:**
- `ServiceNow_Analysis_Complete.md` - ServiceNow analysis demonstrating new format
- Maintained 5-agent structure with improved orchestration
- 50-70% cost reduction vs AutoGen

**Key Improvements:**
- More efficient token usage
- Cleaner output formatting
- Better agent task delegation
- Structured markdown reports

---

### Version 3: CrewAI Refinement - February 2026

Further refinement of agent outputs with per-agent text files.

**Files:**
- `analysis_NVDA_20260205_212556.txt` - Final synthesis report
- `analysis_NVDA_20260205_212556_quality.txt` - Quality Agent output
- `analysis_NVDA_20260205_212556_value.txt` - Valuation Agent output
- `analysis_NVDA_20260205_212556_technical.txt` - Technical Agent output
- `analysis_NVDA_20260205_212556_sentiment.txt` - Sentiment Agent output
- `analysis_NVDA_20260205_212556_catalyst.txt` - Catalyst Agent output

**Key Features:**
- Separate files per agent for transparency
- More detailed agent-level analysis
- Improved evidence citations
- Production-ready format for institutional use

---

### Version 4: Investment-Committee-Lite (Current)

Public-ready educational demo with 4 agents (NO CatalystAgent - Primer-specific).

**What Changed:**
- Removed CatalystAgent (proprietary to production system)
- Simplified to 4 specialist agents (Fundamentals, Valuation, Technical, Sentiment)
- Added mock mode for testing without API keys
- 2-stage DCF (simplified from production 4-stage)
- Educational disclaimers throughout
- Pydantic schemas for type-safe JSON
- Provider-agnostic (OpenAI + Anthropic)

**To Generate New Examples:**
```bash
# Mock mode (no API keys required)
uv run committee-lite analyze TICKER --mock --json

# Real mode with OpenAI/Anthropic
uv run committee-lite analyze TICKER --json

# With lower threshold to trigger debate
uv run committee-lite analyze TICKER --threshold 10 --json
```

---

## Key Insights from Examples

### 1. Disagreement is Expected
- Valuation agents are typically more conservative than fundamentals agents
- Technical agents focus on short-term signals vs long-term fundamentals
- Score spreads of 40-90 points are common for growth stocks

### 2. Reconciliation Adds Value
- Agents update scores ~30% of the time after seeing peer perspectives
- Dissenting views are explicitly documented
- Final decisions incorporate multi-dimensional analysis

### 3. Evidence-Based Analysis
- All agents cite specific data sources (financials, technical indicators, analyst consensus)
- Rationale includes exact numbers and metrics
- Invalidation criteria provide clear risk checkpoints

---

## Using These Examples

**For Newsletter/Blog:**
- Show how multi-agent systems handle disagreement
- Demonstrate the evolution from prototype to production
- Illustrate different architectural choices (AutoGen vs CrewAI)

**For Learning:**
- Compare agent outputs across versions
- Study how disagreement is resolved
- Understand trade-offs between frameworks

**For Development:**
- Reference output formats when building similar systems
- Learn from agent prompt structures
- Understand debate log schemas

---

**⚠️ IMPORTANT DISCLAIMER**

All analyses in this folder are educational demonstrations only. They are:
- NOT investment advice
- NOT suitable for real trading decisions
- NOT validated against historical performance
- NOT compliant with regulatory requirements

For production investment systems, contact the author for consulting.
