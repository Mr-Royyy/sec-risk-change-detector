"""Event-study analysis for SEC filing dates.

The event study connects NLP risk-change scores to market outcomes. For each
filing, it calculates post-filing returns, realized volatility, benchmark
returns, and abnormal returns.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import timedelta

import pandas as pd

from sec_risk_detector.market_data import MarketDataClient


@dataclass(frozen=True)
class EventStudyConfig:
    """Configuration for event-study windows."""

    windows: tuple[int, ...] = (1, 5, 10, 20)
    pre_vol_window: int = 60
    annualization_factor: int = 252


class EventStudyAnalyzer:
    """Calculate market reactions after SEC filing dates."""

    def __init__(
        self,
        market_client: MarketDataClient | None = None,
        config: EventStudyConfig | None = None,
    ) -> None:
        """Initialize analyzer dependencies."""

        self.market_client = market_client or MarketDataClient()
        self.config = config or EventStudyConfig()

    def analyze(
        self,
        risk_scores_df: pd.DataFrame,
        benchmark_ticker: str = "^GSPC",
    ) -> pd.DataFrame:
        """Add event-study columns to a risk-score DataFrame.

        Args:
            risk_scores_df: Output from RiskChangeAnalyzer.compare_dataframe.
            benchmark_ticker: Benchmark used for abnormal returns.

        Returns:
            Original risk-score rows plus event-study metrics.
        """

        required_columns = {"ticker", "current_filing_date", "final_risk_change_score"}
        missing_columns = required_columns - set(risk_scores_df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        if risk_scores_df.empty:
            return risk_scores_df.copy()

        results: list[pd.DataFrame] = []

        for ticker, ticker_df in risk_scores_df.groupby("ticker", sort=False):
            results.append(
                self._analyze_single_ticker(
                    ticker=str(ticker),
                    risk_scores_df=ticker_df,
                    benchmark_ticker=benchmark_ticker,
                )
            )

        return pd.concat(results, ignore_index=True)

    def _analyze_single_ticker(
        self,
        ticker: str,
        risk_scores_df: pd.DataFrame,
        benchmark_ticker: str,
    ) -> pd.DataFrame:
        """Run event-study analysis for one ticker."""

        filing_dates = pd.to_datetime(risk_scores_df["current_filing_date"]).dt.normalize()

        start_date = filing_dates.min() - timedelta(days=self.config.pre_vol_window * 3)
        end_date = filing_dates.max() + timedelta(days=max(self.config.windows) * 3 + 10)

        prices = self.market_client.get_adjusted_close(ticker, start_date, end_date)
        benchmark_prices = self.market_client.get_adjusted_close(
            benchmark_ticker,
            start_date,
            end_date,
        )

        rows = []

        for _, row in risk_scores_df.iterrows():
            rows.append(
                self._analyze_row(
                    row=row,
                    prices=prices,
                    benchmark_prices=benchmark_prices,
                )
            )

        return pd.DataFrame(rows)

    def _analyze_row(
        self,
        row: pd.Series,
        prices: pd.DataFrame,
        benchmark_prices: pd.DataFrame,
    ) -> dict[str, object]:
        """Calculate event-study metrics for one filing row."""

        output = row.to_dict()
        filing_date = pd.Timestamp(row["current_filing_date"]).normalize()

        event_position = self._first_trading_position_on_or_after(prices, filing_date)
        benchmark_position = self._first_trading_position_on_or_after(
            benchmark_prices,
            filing_date,
        )

        if event_position is None:
            output["event_trading_date"] = None
            output["pre_vol_60d"] = math.nan

            for window in self.config.windows:
                output[f"post_return_{window}d"] = math.nan
                output[f"post_vol_{window}d"] = math.nan
                output[f"benchmark_return_{window}d"] = math.nan
                output[f"abnormal_return_{window}d"] = math.nan

            return output

        event_date = prices.index[event_position]
        output["event_trading_date"] = event_date.date().isoformat()
        output["pre_vol_60d"] = self._pre_event_volatility(prices, event_position)

        for window in self.config.windows:
            post_return = self._horizon_return(prices, event_position, window)
            post_vol = self._post_event_volatility(prices, event_position, window)
            benchmark_return = (
                self._horizon_return(benchmark_prices, benchmark_position, window)
                if benchmark_position is not None
                else math.nan
            )

            output[f"post_return_{window}d"] = post_return
            output[f"post_vol_{window}d"] = post_vol
            output[f"benchmark_return_{window}d"] = benchmark_return
            output[f"abnormal_return_{window}d"] = (
                post_return - benchmark_return
                if not math.isnan(post_return) and not math.isnan(benchmark_return)
                else math.nan
            )

        return output

    @staticmethod
    def _first_trading_position_on_or_after(
        prices: pd.DataFrame,
        filing_date: pd.Timestamp,
    ) -> int | None:
        """Return the first trading-day index position on or after filing_date."""

        position = prices.index.searchsorted(filing_date)

        if position >= len(prices):
            return None

        return int(position)

    def _pre_event_volatility(self, prices: pd.DataFrame, event_position: int) -> float:
        """Annualized realized volatility before the filing event."""

        start_position = max(0, event_position - self.config.pre_vol_window)
        returns = prices["daily_return"].iloc[start_position:event_position].dropna()

        if len(returns) < 2:
            return math.nan

        return float(returns.std() * math.sqrt(self.config.annualization_factor))

    def _post_event_volatility(
        self,
        prices: pd.DataFrame,
        event_position: int,
        window: int,
    ) -> float:
        """Annualized realized volatility after the filing event."""

        start_position = event_position + 1
        end_position = event_position + window + 1
        returns = prices["daily_return"].iloc[start_position:end_position].dropna()

        if len(returns) < 2:
            return math.nan

        return float(returns.std() * math.sqrt(self.config.annualization_factor))

    @staticmethod
    def _horizon_return(
        prices: pd.DataFrame,
        event_position: int | None,
        window: int,
    ) -> float:
        """Return percentage return from event date to event date plus window."""

        if event_position is None:
            return math.nan

        horizon_position = event_position + window

        if horizon_position >= len(prices):
            return math.nan

        start_price = prices["adjusted_close"].iloc[event_position]
        end_price = prices["adjusted_close"].iloc[horizon_position]

        if start_price == 0:
            return math.nan

        return float(end_price / start_price - 1)