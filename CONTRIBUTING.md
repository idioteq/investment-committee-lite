# Contributing to Investment Committee Lite

Thank you for your interest in contributing! This is an educational demo project with specific scope boundaries.

## Scope & Boundaries

### ✅ In Scope (Welcome Contributions)

- **Additional agents**: New specialist agents (e.g., MacroAgent, ESGAgent) following existing patterns
- **Improved tools**: Better technical indicators, enhanced DCF assumptions, additional data sources
- **Better prompts**: Clearer agent instructions, improved JSON extraction
- **Documentation**: Examples, tutorials, architecture explanations
- **Tests**: Additional test coverage, edge cases
- **Bug fixes**: Parsing errors, schema validation issues, mock mode problems
- **Performance**: Optimization without adding complexity

### ❌ Out of Scope (Will Not Accept)

- **Real-money trading**: No broker integration, order execution, or position management
- **Backtesting frameworks**: This is a demo, not a production quant system
- **Complex dependencies**: Keep it lightweight (no heavy ML libraries, no databases)
- **Proprietary features**: No firm-specific tools, no non-public data sources
- **Production infrastructure**: No web servers, no cloud deployment configs, no monitoring

## How to Contribute

### 1. Report Issues

Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment (Python version, OS, mock vs real mode)

### 2. Suggest Enhancements

Have an idea? Open an issue with:
- Clear description of the proposed feature
- Why it's valuable for education/demo purposes
- How it fits within scope boundaries
- Optional: pseudocode or design sketch

### 3. Submit Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes:
   - Follow existing code style (use `ruff` for linting)
   - Add tests for new functionality
   - Update documentation if needed
4. Run tests: `uv run pytest`
5. Commit with clear message
6. Push to your fork
7. Open a pull request

## Code Standards

- **Python 3.11+** required
- **Type hints** for all function signatures
- **Docstrings** for all public functions/classes
- **Pydantic** for all data schemas
- **Tests** for all new functionality
- **Simple** over clever

## Agent Design Patterns

If adding a new agent, follow this structure:

```python
class MyNewAgent:
    """One-line description."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.agent_name = "MyName"

    def analyze(self, ticker: str) -> AgentOutput:
        """Analyze and return structured output."""
        # 1. Fetch data
        # 2. Build prompts
        # 3. Call LLM
        # 4. Parse response to AgentOutput
        pass
```

## Tool Design Patterns

If adding a new tool, follow this structure:

```python
def my_new_tool(ticker: str) -> Dict[str, Any]:
    """
    Description of what this tool does.

    Args:
        ticker: Stock ticker

    Returns:
        Dictionary with results
    """
    try:
        # Fetch data
        # Calculate metrics
        return {"ticker": ticker, ...}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}
```

## Questions?

Open an issue with the "question" label.

## Attribution

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**For commercial/production use cases**, contact the author for consulting engagements.
This demo is for educational purposes only and not suitable for managing real money.
