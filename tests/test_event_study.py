"""Tests for event-study analysis."""

from __future__ import annotations

import pandas as pd

from sec_risk_detector.event_study import EventStudyAnalyzer


class FakeMarketDataClient:
    """Test double that returns deterministic price data."""

    def __init__(self) -> None:
        dates = pd.bdate_range("2024-01-01", periods=120)
        prices = pd.DataFrame(index=dates)
        prices["adjusted_close"] = [100 + index for index in range(len(dates))]
        prices["daily_return"] = prices["adjusted_close"].pct_change()
        self.prices = prices

    def get_adjusted_close(
        self,
        ticker: str,
        start_date: object,
        end_date: object,
    ) -> pd.DataFrame:
        """Return the same deterministic price data for any ticker."""

        return self.prices.copy()


def test_event_study_adds_return_and_volatility_columns() -> None:
    """Analyzer should add event-study metrics to risk-score rows."""

    risk_scores_df = pd.DataFrame(
        [
            {
                "ticker": "TEST",
                "current_filing_date": "2024-03-01",
                "final_risk_change_score": 0.75,
            }
        ]
    )

    analyzer = EventStudyAnalyzer(market_client=FakeMarketDataClient())
    result = analyzer.analyze(risk_scores_df)

    assert len(result) == 1
    assert "event_trading_date" in result.columns
    assert "pre_vol_60d" in result.columns
    assert "post_return_5d" in result.columns
    assert "post_vol_5d" in result.columns
    assert "abnormal_return_5d" in result.columns
    assert pd.notna(result.loc[0, "post_return_5d"])


def test_event_study_requires_needed_columns() -> None:
    """Analyzer should fail clearly when required columns are missing."""

    bad_df = pd.DataFrame([{"ticker": "TEST"}])
    analyzer = EventStudyAnalyzer(market_client=FakeMarketDataClient())

    try:
        analyzer.analyze(bad_df)
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing columns")