from datetime import date

from sec_risk_detector.models import Company, Filing


def test_filing_urls_are_constructed_correctly() -> None:
    company = Company(ticker="AAPL", cik="0000320193", name="Apple Inc.")
    filing = Filing(
        company=company,
        form_type="10-K",
        filing_date=date(2024, 11, 1),
        report_date=date(2024, 9, 28),
        accession_number="0000320193-24-000123",
        primary_document="aapl-20240928.htm",
    )

    assert filing.accession_no_dashes == "000032019324000123"
    assert "Archives/edgar/data/320193/000032019324000123" in filing.filing_url
    assert filing.filing_url.endswith("aapl-20240928.htm")
