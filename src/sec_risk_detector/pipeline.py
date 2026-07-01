"""High-level project pipelines.

Pipelines coordinate lower-level objects. The goal is for notebooks, CLIs, and
future dashboards to call a small number of readable methods instead of copying
business logic everywhere.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sec_risk_detector.config import ProjectConfig
from sec_risk_detector.event_study import EventStudyAnalyzer
from sec_risk_detector.models import ExtractedSection
from sec_risk_detector.nlp_features import RiskChangeAnalyzer
from sec_risk_detector.sec_client import SecClient
from sec_risk_detector.section_extractor import RiskSectionExtractor
from sec_risk_detector.research_summary import ResearchSummaryAnalyzer

class FilingIngestionPipeline:
    """Pipeline for ticker lookup, filing metadata, risk extraction, scoring, and event studies."""

    def __init__(
        self,
        client: SecClient | None = None,
        extractor: RiskSectionExtractor | None = None,
        analyzer: RiskChangeAnalyzer | None = None,
        event_analyzer: EventStudyAnalyzer | None = None,
        summary_analyzer: ResearchSummaryAnalyzer | None = None,
    ) -> None:
        """Initialize pipeline dependencies."""

        config = ProjectConfig.from_env()
        self.client = client or SecClient(config)
        self.extractor = extractor or RiskSectionExtractor()
        self.analyzer = analyzer or RiskChangeAnalyzer()
        self.event_analyzer = event_analyzer or EventStudyAnalyzer()
        self.summary_analyzer = summary_analyzer or ResearchSummaryAnalyzer()

    def get_filing_metadata(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 10,
    ) -> pd.DataFrame:
        """Return recent filing metadata as a DataFrame."""

        filings = self.client.get_recent_filings(ticker=ticker, forms=forms, limit=limit)
        return pd.DataFrame([filing.to_dict() for filing in filings])

    def extract_risk_sections(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 5,
    ) -> list[ExtractedSection]:
        """Download recent filings and extract their risk-factor sections."""

        filings = self.client.get_recent_filings(ticker=ticker, forms=forms, limit=limit)
        sections: list[ExtractedSection] = []

        for filing in filings:
            html = self.client.get_text(filing.filing_url)
            section = self.extractor.extract_from_html(filing, html)
            sections.append(section)

        return sections

    def extract_risk_sections_df(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 5,
    ) -> pd.DataFrame:
        """Download filings, extract risk sections, and return a DataFrame."""

        sections = self.extract_risk_sections(ticker=ticker, forms=forms, limit=limit)
        return pd.DataFrame([section.to_dict() for section in sections])

    def build_risk_change_scores_df(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 6,
        compare_mode: str = "previous",
    ) -> pd.DataFrame:
        """Extract risk sections and compute risk-change scores between filings."""

        sections_df = self.extract_risk_sections_df(
            ticker=ticker,
            forms=forms,
            limit=limit,
        )

        return self.analyzer.compare_dataframe(
            sections_df,
            compare_mode=compare_mode,
        )

    def build_event_study_df(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
        benchmark_ticker: str = "^GSPC",
    ) -> pd.DataFrame:
        """Build risk-change scores and add post-filing market outcomes."""

        risk_scores_df = self.build_risk_change_scores_df(
            ticker=ticker,
            forms=forms,
            limit=limit,
            compare_mode=compare_mode,
        )

        return self.event_analyzer.analyze(
            risk_scores_df,
            benchmark_ticker=benchmark_ticker,
        )


    def build_research_summary_df(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
        benchmark_ticker: str = "^GSPC",
    ) -> pd.DataFrame:
        """Build event-study results and summarize outcomes by risk bucket."""

        event_study_df = self.build_event_study_df(
            ticker=ticker,
            forms=forms,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark_ticker,
        )

        return self.summary_analyzer.summarize(event_study_df)

    def build_top_risk_events_df(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
        benchmark_ticker: str = "^GSPC",
        n: int = 10,
    ) -> pd.DataFrame:
        """Build event-study results and return the highest risk-change events."""

        event_study_df = self.build_event_study_df(
            ticker=ticker,
            forms=forms,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark_ticker,
        )

        return self.summary_analyzer.top_risk_events(event_study_df, n=n)
    


    def build_batch_event_study_df(
        self,
        tickers: list[str],
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
        benchmark_ticker: str = "^GSPC",
    ) -> pd.DataFrame:
        """Build event-study results for multiple tickers.

        Args:
            tickers: List of company ticker symbols.
            forms: SEC form types to include.
            limit: Maximum number of filings per ticker.
            compare_mode: Either "previous" or "same-form".
            benchmark_ticker: Benchmark used for abnormal returns.

        Returns:
            Combined event-study DataFrame across all successful tickers.

        Notes:
            If one ticker fails, the method continues with the remaining tickers.
            The error is stored in an error row so the batch run is easier to debug.
        """

        frames: list[pd.DataFrame] = []

        for ticker in tickers:
            clean_ticker = ticker.upper().strip()

            if not clean_ticker:
                continue

            try:
                ticker_df = self.build_event_study_df(
                    ticker=clean_ticker,
                    forms=forms,
                    limit=limit,
                    compare_mode=compare_mode,
                    benchmark_ticker=benchmark_ticker,
                )
                frames.append(ticker_df)

            except Exception as exc:  # noqa: BLE001
                error_df = pd.DataFrame(
                    [
                        {
                            "ticker": clean_ticker,
                            "error": str(exc),
                        }
                    ]
                )
                frames.append(error_df)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def build_batch_research_summary_df(
        self,
        tickers: list[str],
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
        benchmark_ticker: str = "^GSPC",
    ) -> pd.DataFrame:
        """Build multi-ticker event-study results and summarize by risk bucket."""

        event_study_df = self.build_batch_event_study_df(
            tickers=tickers,
            forms=forms,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark_ticker,
        )

        valid_df = event_study_df.dropna(subset=["final_risk_change_score"], how="any")

        if valid_df.empty:
            return pd.DataFrame()

        return self.summary_analyzer.summarize(valid_df)

    def build_batch_top_risk_events_df(
        self,
        tickers: list[str],
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
        benchmark_ticker: str = "^GSPC",
        n: int = 10,
    ) -> pd.DataFrame:
        """Build multi-ticker event-study results and return top risk events."""

        event_study_df = self.build_batch_event_study_df(
            tickers=tickers,
            forms=forms,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark_ticker,
        )

        valid_df = event_study_df.dropna(subset=["final_risk_change_score"], how="any")

        if valid_df.empty:
            return pd.DataFrame()

        return self.summary_analyzer.top_risk_events(valid_df, n=n)
    
    @staticmethod
    def save_dataframe(df: pd.DataFrame, output_path: str | Path) -> Path:
        """Save a DataFrame to CSV, creating parent directories as needed."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path