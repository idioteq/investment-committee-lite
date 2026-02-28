"""Command-line interface for Investment Committee Lite."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from committee_lite.config import Config
from committee_lite.orchestrator import InvestmentCommittee
from committee_lite.llm import get_llm_client


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Investment Committee Lite - Multi-agent stock analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis in mock mode (no API keys needed)
  committee-lite analyze NVDA --mock

  # Run with OpenAI (requires OPENAI_API_KEY in .env)
  committee-lite analyze AAPL --provider openai

  # Run with Anthropic and save JSON
  committee-lite analyze TSLA --provider anthropic --json

  # Adjust disagreement threshold
  committee-lite analyze MSFT --threshold 20

⚠️  EDUCATIONAL DEMO ONLY - NOT INVESTMENT ADVICE
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a stock')
    analyze_parser.add_argument('ticker', help='Stock ticker symbol')
    analyze_parser.add_argument(
        '--provider',
        choices=['openai', 'anthropic'],
        help='LLM provider (default: from .env or openai)'
    )
    analyze_parser.add_argument(
        '--model',
        help='Model name (default: from .env)'
    )
    analyze_parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock mode (no API keys needed)'
    )
    analyze_parser.add_argument(
        '--threshold',
        type=int,
        help=f'Disagreement threshold (default: {Config.DISAGREEMENT_THRESHOLD})'
    )
    analyze_parser.add_argument(
        '--max-rounds',
        type=int,
        help=f'Max reconciliation rounds (default: {Config.MAX_RECONCILE_ROUNDS})'
    )
    analyze_parser.add_argument(
        '--json',
        action='store_true',
        help='Save output as JSON'
    )
    analyze_parser.add_argument(
        '--max-tokens',
        type=int,
        default=2000,
        help='Max tokens per LLM call (default: 2000)'
    )
    analyze_parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='LLM temperature (default: 0.7)'
    )

    args = parser.parse_args()

    if args.command == 'analyze':
        run_analysis(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_analysis(args):
    """Run investment committee analysis."""

    print("\n" + "="*80)
    print("INVESTMENT COMMITTEE LITE")
    print("="*80)
    print("⚠️  EDUCATIONAL DEMO ONLY - NOT INVESTMENT ADVICE")
    print("="*80 + "\n")

    ticker = args.ticker.upper()

    # Determine mode
    if args.mock:
        print(f"Mode: MOCK (using canned responses)\n")
        llm_client = get_llm_client(mock=True)
    else:
        # Validate config
        try:
            Config.validate()
            provider = args.provider or Config.LLM_PROVIDER
            model = args.model or Config.get_active_model()
            print(f"Mode: REAL")
            print(f"Provider: {provider}")
            print(f"Model: {model}\n")
            llm_client = get_llm_client(provider=provider, model=model)
        except ValueError as e:
            print(f"Configuration Error: {e}")
            print("\nEither:")
            print("  1. Set API keys in .env file (copy from .env.example)")
            print("  2. Use --mock flag for demo mode")
            sys.exit(1)

    # Create committee
    committee = InvestmentCommittee(
        llm_client=llm_client,
        disagreement_threshold=args.threshold,
        max_reconcile_rounds=args.max_rounds,
    )

    # Run analysis
    try:
        decision = committee.analyze(ticker)

        # Print decision packet
        print("\n" + str(decision))

        # Save outputs if requested
        if args.json:
            save_outputs(ticker, decision)

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def save_outputs(ticker: str, decision):
    """Save analysis outputs to files."""
    # Create outputs directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_path = output_dir / f"{ticker}_{timestamp}.json"
    with open(json_path, 'w') as f:
        # Convert to dict for JSON serialization
        json.dump(decision.model_dump(), f, indent=2, default=str)

    print(f"\n💾 Saved JSON: {json_path}")

    # Save text decision packet
    txt_path = output_dir / f"{ticker}_{timestamp}_decision.txt"
    with open(txt_path, 'w') as f:
        f.write(str(decision))

    print(f"💾 Saved decision packet: {txt_path}")


if __name__ == "__main__":
    main()
