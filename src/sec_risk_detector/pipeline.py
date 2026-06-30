"""High-level project pipelines.

Pipelines coordinate lower-level objects. The goal is for notebooks, CLIs, and
future dashboards to call a small number of readable methods instead of copying
business logic everywhere.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sec_risk_detector.config import ProjectConfig
from sec_risk_detector.models import ExtractedSection
from sec_risk_detector.nlp_features import RiskChangeAnalyzer
from sec_risk_detector.sec_client import SecClient
from sec_risk_detector.section_extractor import RiskSectionExtractor


class FilingIngestionPipeline:
    """Pipeline for ticker lookup, filing metadata, risk extraction, and scoring."""

    def __init__(
        self,
        client: SecClient | None = None,
        extractor: RiskSectionExtractor | None = None,
        analyzer: RiskChangeAnalyzer | None = None,
    ) -> None:
        """Initialize pipeline dependencies."""

        config = ProjectConfig.from_env()
        self.client = client or SecClient(config)
        self.extractor = extractor or RiskSectionExtractor()
        self.analyzer = analyzer or RiskChangeAnalyzer()

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
        """Extract risk sections and compute risk-change scores between filings.

        Args:
            ticker: Company ticker symbol.
            forms: SEC form types to include.
            limit: Maximum number of filings to fetch.
            compare_mode: Either "previous" or "same-form".

        Returns:
            A DataFrame of risk-change scores.
        """

        sections_df = self.extract_risk_sections_df(
            ticker=ticker,
            forms=forms,
            limit=limit,
        )

        return self.analyzer.compare_dataframe(
            sections_df,
            compare_mode=compare_mode,
        )

    @staticmethod
    def save_dataframe(df: pd.DataFrame, output_path: str | Path) -> Path:
        """Save a DataFrame to CSV, creating parent directories as needed."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path