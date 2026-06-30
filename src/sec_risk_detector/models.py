"""Data models used across the project.

The project uses small dataclasses instead of loose dictionaries so that the
rest of the codebase has predictable attributes and fewer duplicate parsing
functions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class Company:
    """A public company mapped from ticker to SEC CIK.

    Attributes:
        ticker: Stock ticker symbol, uppercased.
        cik: SEC Central Index Key as a zero-padded 10-character string.
        name: EDGAR conformed company name.
    """

    ticker: str
    cik: str
    name: str

    @property
    def cik_int(self) -> int:
        """Return the CIK as an integer for EDGAR archive URLs."""

        return int(self.cik)

    def to_dict(self) -> dict[str, str]:
        """Convert the company object to a dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class Filing:
    """Metadata for one SEC filing.

    Attributes:
        company: Company object associated with the filing.
        form_type: Filing form type, such as 10-K or 10-Q.
        filing_date: Date the filing was filed.
        report_date: Reporting period date when available.
        accession_number: SEC accession number with dashes.
        primary_document: Main filing HTML document name.
    """

    company: Company
    form_type: str
    filing_date: date
    report_date: date | None
    accession_number: str
    primary_document: str

    @property
    def accession_no_dashes(self) -> str:
        """Return accession number without dashes for EDGAR archive paths."""

        return self.accession_number.replace("-", "")

    @property
    def filing_url(self) -> str:
        """Return the direct URL to the filing's primary document."""

        return (
            "https://www.sec.gov/Archives/edgar/data/"
            f"{self.company.cik_int}/{self.accession_no_dashes}/{self.primary_document}"
        )

    @property
    def index_url(self) -> str:
        """Return the SEC filing detail page URL."""

        return (
            "https://www.sec.gov/Archives/edgar/data/"
            f"{self.company.cik_int}/{self.accession_no_dashes}/"
            f"{self.accession_number}-index.html"
        )

    def to_dict(self) -> dict[str, object]:
        """Flatten filing metadata into a DataFrame-friendly dictionary."""

        return {
            "ticker": self.company.ticker,
            "company_name": self.company.name,
            "cik": self.company.cik,
            "form_type": self.form_type,
            "filing_date": self.filing_date.isoformat(),
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "accession_number": self.accession_number,
            "primary_document": self.primary_document,
            "filing_url": self.filing_url,
            "index_url": self.index_url,
        }


@dataclass(frozen=True)
class ExtractedSection:
    """Text extracted from a filing section.

    Attributes:
        filing: Filing metadata object.
        section_name: Human-readable section name.
        text: Cleaned section text.
        word_count: Approximate word count of extracted text.
        extraction_quality: Simple quality flag: good, short, missing, or suspiciously_long.
    """

    filing: Filing
    section_name: str
    text: str
    word_count: int
    extraction_quality: str

    def to_dict(self) -> dict[str, object]:
        """Flatten extracted section data into a DataFrame-friendly dictionary."""

        data = self.filing.to_dict()
        data.update(
            {
                "section_name": self.section_name,
                "risk_text": self.text,
                "risk_word_count": self.word_count,
                "extraction_quality": self.extraction_quality,
            }
        )
        return data
