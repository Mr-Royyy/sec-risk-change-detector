"""Command-line interface for the SEC Risk Change Detector MVP."""

from __future__ import annotations

import argparse
from pathlib import Path

from sec_risk_detector.pipeline import FilingIngestionPipeline


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description="Fetch SEC filing metadata and optionally analyze risk-factor text."
    )

    parser.add_argument("ticker", help="Ticker symbol, for example AAPL or MSFT.")

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of filings to return.",
    )

    parser.add_argument(
        "--forms",
        nargs="+",
        default=["10-K", "10-Q"],
        help="Form types to include, for example: 10-K 10-Q",
    )

    parser.add_argument(
        "--extract-risk",
        action="store_true",
        help="Download filings and extract Item 1A risk-factor text.",
    )

    parser.add_argument(
        "--score-risk",
        action="store_true",
        help="Extract risk text and compute risk-change scores against previous filings.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional CSV output path.",
    )

    return parser


def main() -> None:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args()

    pipeline = FilingIngestionPipeline()
    forms = tuple(args.forms)

    if args.score_risk:
        df = pipeline.build_risk_change_scores_df(
            args.ticker,
            forms=forms,
            limit=args.limit,
        )
    elif args.extract_risk:
        df = pipeline.extract_risk_sections_df(
            args.ticker,
            forms=forms,
            limit=args.limit,
        )
    else:
        df = pipeline.get_filing_metadata(
            args.ticker,
            forms=forms,
            limit=args.limit,
        )

    print(df.drop(columns=["risk_text"], errors="ignore").to_string(index=False))

    if args.output:
        saved_path = pipeline.save_dataframe(df, args.output)
        print(f"\nSaved output to {saved_path}")


if __name__ == "__main__":
    main()