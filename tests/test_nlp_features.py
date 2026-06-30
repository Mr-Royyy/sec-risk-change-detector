"""Tests for risk-change feature generation."""

from __future__ import annotations

import pandas as pd

from sec_risk_detector.nlp_features import (
    RiskChangeAnalyzer,
    RiskTextPreprocessor,
    UNCERTAINTY_TERMS,
)


def test_tokenizer_removes_noise_words_but_uncertainty_rate_counts_may() -> None:
    """Tokenizer removes noise words while uncertainty rates still count 'may'."""

    preprocessor = RiskTextPreprocessor()

    text = "The company may face supply disruption and adverse claims."
    tokens = preprocessor.tokenize(text)
    uncertainty_rate = preprocessor.term_rate_per_1000_words(text, UNCERTAINTY_TERMS)

    assert "company" not in tokens
    assert "disruption" in tokens
    assert "adverse" in tokens
    assert uncertainty_rate > 0


def test_compare_dataframe_generates_one_less_row_than_filings() -> None:
    """Three filings should produce two current-vs-previous comparisons."""

    sections_df = pd.DataFrame(
        [
            {
                "ticker": "TEST",
                "filing_date": "2024-01-01",
                "form_type": "10-K",
                "accession_number": "0001",
                "risk_word_count": 10,
                "risk_text": "Supply chains may create delays and uncertainty.",
            },
            {
                "ticker": "TEST",
                "filing_date": "2025-01-01",
                "form_type": "10-K",
                "accession_number": "0002",
                "risk_word_count": 14,
                "risk_text": "Supply chains may create delays, uncertainty, disruption, and losses.",
            },
            {
                "ticker": "TEST",
                "filing_date": "2026-01-01",
                "form_type": "10-K",
                "accession_number": "0003",
                "risk_word_count": 16,
                "risk_text": "Supply chains may create severe disruption, losses, volatility, and claims.",
            },
        ]
    )

    result = RiskChangeAnalyzer().compare_dataframe(sections_df)

    assert len(result) == 2
    assert "final_risk_change_score" in result.columns
    assert result["final_risk_change_score"].between(0, 1).all()


def test_compare_dataframe_requires_needed_columns() -> None:
    """Analyzer should fail clearly when the extraction DataFrame is incomplete."""

    sections_df = pd.DataFrame([{"ticker": "TEST"}])

    try:
        RiskChangeAnalyzer().compare_dataframe(sections_df)
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing columns")