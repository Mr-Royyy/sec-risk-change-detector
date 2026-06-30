from datetime import date

from sec_risk_detector.models import Company, Filing
from sec_risk_detector.section_extractor import RiskSectionExtractor


def _sample_filing() -> Filing:
    return Filing(
        company=Company(ticker="TEST", cik="0000000001", name="Test Company"),
        form_type="10-K",
        filing_date=date(2024, 1, 1),
        report_date=date(2023, 12, 31),
        accession_number="0000000001-24-000001",
        primary_document="test.htm",
    )


def test_extracts_item_1a_risk_factors() -> None:
    html = """
    <html><body>
      <h1>Item 1. Business</h1><p>Business section.</p>
      <h1>Item 1A. Risk Factors</h1>
      <p>Our business faces market risk, liquidity risk, and execution risk.</p>
      <p>These risks may materially affect future results.</p>
      <h1>Item 1B. Unresolved Staff Comments</h1><p>None.</p>
    </body></html>
    """
    extractor = RiskSectionExtractor()
    section = extractor.extract_from_html(_sample_filing(), html)

    assert "Risk Factors" in section.text
    assert "liquidity risk" in section.text
    assert "Unresolved Staff Comments" not in section.text
    assert section.extraction_quality in {"short", "good"}


def test_missing_risk_section_returns_missing_quality() -> None:
    html = "<html><body><h1>Item 1. Business</h1><p>No risk heading here.</p></body></html>"
    extractor = RiskSectionExtractor()
    section = extractor.extract_from_html(_sample_filing(), html)

    assert section.text == ""
    assert section.extraction_quality == "missing"
