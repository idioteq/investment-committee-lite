# Examples

This directory contains sample outputs from the Investment Committee Lite system.

## Contents

Example analyses demonstrating the multi-agent investment committee in action:

- **JSON outputs**: Complete structured decision packets with all agent scores, rationale, and debate logs
- **Decision reports**: Formatted text reports showing the final investment decision
- **Debate logs**: Examples of disagreement reconciliation between agents

## Purpose

These examples illustrate:
- How the 4 specialist agents (Fundamentals, Valuation, Technical, Sentiment) analyze stocks
- How the Portfolio Manager synthesizes their views into final decisions
- How disagreement handling works when agents have divergent scores
- The complete output format including rationale, action plans, and invalidation criteria

## Usage

To generate your own examples:

```bash
# Mock mode (no API keys required)
uv run committee-lite analyze TICKER --mock --json

# With disagreement threshold to trigger debate
uv run committee-lite analyze TICKER --mock --threshold 5 --json
```

Examples are saved to `outputs/` directory and can be copied here for documentation purposes.

---

**Note**: All examples are generated using mock mode with canned responses for demonstration purposes. This is an educational demo - not investment advice.
