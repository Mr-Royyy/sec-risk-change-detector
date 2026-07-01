"""Tests for research summary generation."""

from __future__ import annotations

import pandas as pd

from sec_risk_detector.research_summary import ResearchSummaryAnalyzer


def test_research_summary_groups_by_risk_bucket() -> None:
    """Summary analyzer should create low/medium/high bucket rows."""

    event_study_df = pd.DataFrame(
        [
            {
                "ticker": "TEST",
                "current_filing_date": "2024-01-01",
                "current_form_type": "10-Q",
                "final_risk_change_score": 0.10,
                "post_return_5d": 0.01,
                "post_return_20d": 0.02,
                "post_vol_5d": 0.20,
                "post_vol_20d": 0.25,
                "abnormal_return_5d": 0.005,
                "abnormal_return_20d": 0.010,
            },
            {
                "ticker": "TEST",
                "current_filing_date": "2024-04-01",
                "current_form_type": "10-Q",
                "final_risk_change_score": 0.50,
                "post_return_5d": -0.01,
                "post_return_20d": -0.03,
                "post_vol_5d": 0.30,
                "post_vol_20d": 0.35,
                "abnormal_return_5d": -0.015,
                "abnormal_return_20d": -0.040,
            },
            {
                "ticker": "TEST",
                "current_filing_date": "2024-07-01",
                "current_form_type": "10-Q",
                "final_risk_change_score": 0.90,
                "post_return_5d": -0.05,
                "post_return_20d": -0.08,
                "post_vol_5d": 0.40,
                "post_vol_20d": 0.50,
                "abnormal_return_5d": -0.060,
                "abnormal_return_20d": -0.090,
            },
        ]
    )

    summary = ResearchSummaryAnalyzer().summarize(event_study_df)

    assert len(summary) == 3
    assert "risk_score_bucket" in summary.columns
    assert "avg_risk_change_score" in summary.columns
    assert "avg_post_vol_20d" in summary.columns


def test_top_risk_events_returns_highest_scores_first() -> None:
    """Top event table should sort by risk-change score descending."""

    event_study_df = pd.DataFrame(
        [
            {
                "ticker": "TEST",
                "current_filing_date": "2024-01-01",
                "current_form_type": "10-Q",
                "previous_filing_date": "2023-10-01",
                "previous_form_type": "10-Q",
                "final_risk_change_score": 0.20,
                "post_return_5d": 0.01,
                "post_return_20d": 0.02,
                "abnormal_return_5d": 0.01,
                "abnormal_return_20d": 0.02,
                "post_vol_5d": 0.20,
                "post_vol_20d": 0.25,
                "top_added_terms": "supply, claims",
            },
            {
                "ticker": "TEST",
                "current_filing_date": "2024-04-01",
                "current_form_type": "10-Q",
                "previous_filing_date": "2024-01-01",
                "previous_form_type": "10-Q",
                "final_risk_change_score": 0.90,
                "post_return_5d": -0.03,
                "post_return_20d": -0.04,
                "abnormal_return_5d": -0.04,
                "abnormal_return_20d": -0.05,
                "post_vol_5d": 0.45,
                "post_vol_20d": 0.55,
                "top_added_terms": "volatility, disruption",
            },
        ]
    )

    top_events = ResearchSummaryAnalyzer().top_risk_events(event_study_df, n=1)

    assert len(top_events) == 1
    assert top_events.loc[0, "final_risk_change_score"] == 0.90


def test_research_summary_requires_needed_columns() -> None:
    """Summary analyzer should fail clearly when required columns are missing."""

    bad_df = pd.DataFrame([{"ticker": "TEST"}])

    try:
        ResearchSummaryAnalyzer().summarize(bad_df)
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing columns")