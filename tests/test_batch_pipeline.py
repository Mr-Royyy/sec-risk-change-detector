"""Tests for batch pipeline methods."""

from __future__ import annotations

import pandas as pd

from sec_risk_detector.pipeline import FilingIngestionPipeline


class FakeEventAnalyzer:
    """Fake event analyzer for batch pipeline tests."""

    def analyze(self, risk_scores_df: pd.DataFrame, benchmark_ticker: str = "^GSPC") -> pd.DataFrame:
        """Return the input DataFrame with fake event-study columns."""

        output = risk_scores_df.copy()
        output["post_return_5d"] = 0.01
        output["post_return_20d"] = 0.02
        output["post_vol_5d"] = 0.20
        output["post_vol_20d"] = 0.25
        output["abnormal_return_5d"] = 0.005
        output["abnormal_return_20d"] = 0.010
        return output


class FakeSummaryAnalyzer:
    """Fake summary analyzer for batch pipeline tests."""

    def summarize(self, event_study_df: pd.DataFrame) -> pd.DataFrame:
        """Return a tiny fake summary table."""

        return pd.DataFrame(
            [
                {
                    "risk_score_bucket": "high",
                    "filing_count": len(event_study_df),
                    "avg_risk_change_score": event_study_df["final_risk_change_score"].mean(),
                }
            ]
        )

    def top_risk_events(self, event_study_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """Return highest risk-change rows."""

        return event_study_df.sort_values(
            "final_risk_change_score",
            ascending=False,
        ).head(n)


class FakeBatchPipeline(FilingIngestionPipeline):
    """Pipeline test double that avoids live SEC and market-data calls."""

    def __init__(self) -> None:
        self.event_analyzer = FakeEventAnalyzer()
        self.summary_analyzer = FakeSummaryAnalyzer()

    def build_risk_change_scores_df(
        self,
        ticker: str,
        forms: tuple[str, ...] = ("10-K", "10-Q"),
        limit: int = 8,
        compare_mode: str = "same-form",
    ) -> pd.DataFrame:
        """Return deterministic fake risk scores."""

        return pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "current_filing_date": "2024-01-01",
                    "current_form_type": "10-Q",
                    "previous_filing_date": "2023-10-01",
                    "previous_form_type": "10-Q",
                    "final_risk_change_score": 0.70,
                    "tfidf_change_score": 0.50,
                    "word_count_pct_change": 0.10,
                    "top_added_terms": "supply, volatility",
                }
            ]
        )


def test_batch_event_study_combines_multiple_tickers() -> None:
    """Batch event study should combine results across tickers."""

    pipeline = FakeBatchPipeline()

    result = pipeline.build_batch_event_study_df(
        tickers=["AAA", "BBB"],
        limit=3,
        compare_mode="same-form",
    )

    assert len(result) == 2
    assert set(result["ticker"]) == {"AAA", "BBB"}
    assert "post_return_20d" in result.columns


def test_batch_summary_uses_combined_event_study_results() -> None:
    """Batch summary should summarize combined event-study rows."""

    pipeline = FakeBatchPipeline()

    result = pipeline.build_batch_research_summary_df(
        tickers=["AAA", "BBB"],
        limit=3,
        compare_mode="same-form",
    )

    assert len(result) == 1
    assert result.loc[0, "filing_count"] == 2


def test_batch_top_events_returns_highest_risk_events() -> None:
    """Batch top events should return sorted top events."""

    pipeline = FakeBatchPipeline()

    result = pipeline.build_batch_top_risk_events_df(
        tickers=["AAA", "BBB"],
        limit=3,
        compare_mode="same-form",
        n=1,
    )

    assert len(result) == 1
    assert result.loc[0, "final_risk_change_score"] == 0.70