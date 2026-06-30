"""High-level project pipelines.

Pipelines coordinate lower-level objects. The goal is for notebooks, CLIs, and
future dashboards to call a small number of readable methods instead of copying
business logic everywhere.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sec_risk_detector.config import ProjectConfig
from sec_risk_detector.models import ExtractedSection, Filing
from sec_risk_detector.sec_client import SecClient
from sec_risk_detector.section_extractor import RiskSectionExtractor


class FilingIngestionPipeline:
    """Pipeline for ticker lookup, filing metadata, and risk text extraction."""

    def __init__(
        self,
        client: SecClient | None = None,
        extractor: RiskSectionExtractor | None = None,
    ) -> None:
        config = ProjectConfig.from_env()
        self.client = client or SecClient(config)
        self.extractor = extractor or RiskSectionExtractor()

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
            sections.append(self.extractor.extract_from_html(filing, html))
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

    @staticmethod
    def save_dataframe(df: pd.DataFrame, output_path: str | Path) -> Path:
        """Save a DataFrame to CSV, creating parent directories as needed."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path
