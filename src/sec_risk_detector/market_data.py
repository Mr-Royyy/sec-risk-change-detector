"""Market data access for event-study analysis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class PriceDataRequest:
    """Request parameters for historical adjusted price data."""

    ticker: str
    start_date: date | str
    end_date: date | str


class MarketDataClient:
    """Download and clean daily adjusted price data.

    This class keeps market-data logic separate from the event-study logic. That
    makes the project easier to test because tests can pass in a fake data client.
    """

    def get_adjusted_close(
        self,
        ticker: str,
        start_date: date | str,
        end_date: date | str,
    ) -> pd.DataFrame:
        """Return daily adjusted close prices and daily returns.

        Args:
            ticker: Security ticker, for example "AAPL" or "^GSPC".
            start_date: Start date accepted by pandas/yfinance.
            end_date: End date accepted by pandas/yfinance.

        Returns:
            DataFrame indexed by trading date with columns:
            adjusted_close, daily_return.
        """

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            raise ValueError(f"No market data returned for ticker: {ticker}")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [column[0] for column in data.columns]

        if "Close" not in data.columns:
            raise ValueError(f"Market data for {ticker} does not contain a Close column.")

        prices = pd.DataFrame(index=pd.to_datetime(data.index))
        prices["adjusted_close"] = data["Close"].astype(float)

        if prices.index.tz is not None:
            prices.index = prices.index.tz_localize(None)

        prices.index = prices.index.normalize()
        prices = prices.sort_index()
        prices["daily_return"] = prices["adjusted_close"].pct_change()

        return prices