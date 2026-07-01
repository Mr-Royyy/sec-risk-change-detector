"""Streamlit dashboard for the SEC Risk Change Detector.

The dashboard provides an interactive interface for:
1. SEC filing metadata
2. NLP risk-change scoring
3. Event-study market reaction analysis
4. Research summaries
5. Multi-ticker batch analysis
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from sec_risk_detector.pipeline import FilingIngestionPipeline


DEFAULT_UNIVERSE = "AAPL MSFT NVDA TSLA JPM WMT XOM AMZN META NFLX"


class RiskDashboardApp:
    """Interactive dashboard for SEC risk-change analysis."""

    def __init__(self) -> None:
        """Initialize dashboard dependencies."""

        self.pipeline = FilingIngestionPipeline()

    def run(self) -> None:
        """Render the Streamlit app."""

        st.set_page_config(
            page_title="SEC Risk Change Detector",
            page_icon="📊",
            layout="wide",
        )

        st.title("SEC Risk Change Detector")
        st.caption(
            "Analyze changes in SEC risk-factor language and connect those changes "
            "to post-filing returns, volatility, and abnormal returns."
        )

        controls = self._sidebar_controls()

        tabs = st.tabs(
            [
                "Filing Metadata",
                "Risk Scores",
                "Event Study",
                "Summary",
                "Top Events",
                "Methodology",
            ]
        )

        with tabs[0]:
            self._render_metadata_tab(controls)

        with tabs[1]:
            self._render_scores_tab(controls)

        with tabs[2]:
            self._render_event_study_tab(controls)

        with tabs[3]:
            self._render_summary_tab(controls)

        with tabs[4]:
            self._render_top_events_tab(controls)

        with tabs[5]:
            self._render_methodology_tab()

    def _sidebar_controls(self) -> dict[str, object]:
        """Render sidebar controls and return selected values."""

        st.sidebar.header("Controls")

        mode = st.sidebar.radio(
            "Analysis mode",
            options=["Single ticker", "Batch universe"],
            index=0,
        )

        if mode == "Single ticker":
            ticker_input = st.sidebar.text_input(
                "Ticker",
                value="AAPL",
                help="Enter one public company ticker, such as AAPL, MSFT, TSLA, or NVDA.",
            )
            tickers = [ticker_input.upper().strip()] if ticker_input.strip() else []
        else:
            universe_input = st.sidebar.text_area(
                "Tickers",
                value=DEFAULT_UNIVERSE,
                help="Enter tickers separated by spaces, commas, or new lines.",
                height=120,
            )
            tickers = self._parse_tickers(universe_input)

        limit = st.sidebar.slider(
            "Filings per ticker",
            min_value=3,
            max_value=20,
            value=8,
            step=1,
            help="More filings gives better summaries but takes longer to run.",
        )

        compare_mode = st.sidebar.selectbox(
            "Comparison mode",
            options=["same-form", "previous"],
            index=0,
            help=(
                "same-form compares 10-Q to previous 10-Q and 10-K to previous 10-K. "
                "previous compares to the immediately prior filing regardless of form type."
            ),
        )

        benchmark = st.sidebar.text_input(
            "Benchmark",
            value="^GSPC",
            help="Benchmark ticker used for abnormal returns.",
        ).strip()

        top_n = st.sidebar.slider(
            "Top events to show",
            min_value=1,
            max_value=25,
            value=10,
            step=1,
        )

        st.sidebar.info(
            "For research-style results, use same-form comparison to avoid comparing "
            "long 10-K risk sections directly against shorter 10-Q sections."
        )

        return {
            "mode": mode,
            "tickers": tickers,
            "limit": limit,
            "compare_mode": compare_mode,
            "benchmark": benchmark,
            "top_n": top_n,
        }

    def _render_metadata_tab(self, controls: dict[str, object]) -> None:
        """Render recent SEC filing metadata."""

        st.subheader("Recent SEC Filings")

        tickers = controls["tickers"]
        limit = int(controls["limit"])

        st.write(
            "This tab shows raw filing metadata. Metadata is single-ticker only "
            "because it is mainly used to inspect one company before running deeper analysis."
        )

        if not tickers:
            st.warning("Enter at least one ticker.")
            return

        ticker = tickers[0]

        if st.button("Load Filing Metadata", key="metadata_button"):
            with st.spinner(f"Fetching SEC filing metadata for {ticker}..."):
                df = self._get_metadata(ticker, limit)

            self._display_dataframe_with_download(
                df,
                file_name=f"{ticker.lower()}_filing_metadata.csv",
            )

    def _render_scores_tab(self, controls: dict[str, object]) -> None:
        """Render NLP risk-change scores."""

        st.subheader("Risk Change Scores")

        tickers = controls["tickers"]
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])

        if not tickers:
            st.warning("Enter at least one ticker.")
            return

        if len(tickers) > 1:
            st.info(
                "Risk-score tab is single-ticker for readability. "
                "Use Summary or Top Events for batch analysis."
            )

        ticker = tickers[0]

        if st.button("Calculate Risk Scores", key="scores_button"):
            with st.spinner(f"Extracting risk sections and calculating scores for {ticker}..."):
                df = self._get_scores(ticker, limit, compare_mode)

            self._display_dataframe_with_download(
                df,
                file_name=f"{ticker.lower()}_risk_scores.csv",
            )

            chart_df = self._prepare_date_chart_df(
                df,
                date_column="current_filing_date",
                value_column="final_risk_change_score",
            )

            if not chart_df.empty:
                st.line_chart(
                    chart_df,
                    x="current_filing_date",
                    y="final_risk_change_score",
                )

    def _render_event_study_tab(self, controls: dict[str, object]) -> None:
        """Render event-study results."""

        st.subheader("Post-Filing Market Reaction")

        tickers = controls["tickers"]
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])

        if not tickers:
            st.warning("Enter at least one ticker.")
            return

        button_label = "Run Batch Event Study" if len(tickers) > 1 else "Run Event Study"

        if st.button(button_label, key="event_button"):
            with st.spinner("Running event study..."):
                if len(tickers) > 1:
                    df = self.pipeline.build_batch_event_study_df(
                        tickers=tickers,
                        limit=limit,
                        compare_mode=compare_mode,
                        benchmark_ticker=benchmark,
                    )
                    file_name = "batch_event_study.csv"
                else:
                    df = self._get_event_study(
                        tickers[0],
                        limit,
                        compare_mode,
                        benchmark,
                    )
                    file_name = f"{tickers[0].lower()}_event_study.csv"

            self._display_dataframe_with_download(df, file_name=file_name)

            numeric_columns = [
                column
                for column in [
                    "final_risk_change_score",
                    "post_return_20d",
                    "abnormal_return_20d",
                    "post_vol_20d",
                ]
                if column in df.columns
            ]

            if numeric_columns:
                st.write("Key event-study fields:")

                display_columns = [
                    column
                    for column in [
                        "ticker",
                        "current_filing_date",
                        "current_form_type",
                        *numeric_columns,
                    ]
                    if column in df.columns
                ]

                st.dataframe(df[display_columns], use_container_width=True)

    def _render_summary_tab(self, controls: dict[str, object]) -> None:
        """Render research summary by risk-score bucket."""

        st.subheader("Research Summary by Risk Score Bucket")

        tickers = controls["tickers"]
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])

        if not tickers:
            st.warning("Enter at least one ticker.")
            return

        if st.button("Build Summary", key="summary_button"):
            with st.spinner("Building research summary..."):
                if len(tickers) > 1:
                    df = self.pipeline.build_batch_research_summary_df(
                        tickers=tickers,
                        limit=limit,
                        compare_mode=compare_mode,
                        benchmark_ticker=benchmark,
                    )
                    file_name = "batch_summary.csv"
                else:
                    df = self._get_summary(
                        tickers[0],
                        limit,
                        compare_mode,
                        benchmark,
                    )
                    file_name = f"{tickers[0].lower()}_summary.csv"

            self._display_dataframe_with_download(df, file_name=file_name)

            if not df.empty and "avg_post_vol_20d" in df.columns:
                st.bar_chart(df, x="risk_score_bucket", y="avg_post_vol_20d")

            if not df.empty and "avg_abnormal_return_20d" in df.columns:
                st.bar_chart(df, x="risk_score_bucket", y="avg_abnormal_return_20d")

            st.caption(
                "Interpret small samples carefully. A one-company run validates the pipeline; "
                "a larger batch universe gives more useful research evidence."
            )

    def _render_top_events_tab(self, controls: dict[str, object]) -> None:
        """Render highest risk-change filing events."""

        st.subheader("Top Risk-Change Events")

        tickers = controls["tickers"]
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])
        top_n = int(controls["top_n"])

        if not tickers:
            st.warning("Enter at least one ticker.")
            return

        if st.button("Find Top Events", key="top_events_button"):
            with st.spinner("Finding top risk-change events..."):
                if len(tickers) > 1:
                    df = self.pipeline.build_batch_top_risk_events_df(
                        tickers=tickers,
                        limit=limit,
                        compare_mode=compare_mode,
                        benchmark_ticker=benchmark,
                        n=top_n,
                    )
                    file_name = "batch_top_events.csv"
                else:
                    df = self.pipeline.build_top_risk_events_df(
                        ticker=tickers[0],
                        limit=limit,
                        compare_mode=compare_mode,
                        benchmark_ticker=benchmark,
                        n=top_n,
                    )
                    file_name = f"{tickers[0].lower()}_top_events.csv"

            self._display_dataframe_with_download(df, file_name=file_name)

    def _render_methodology_tab(self) -> None:
        """Render a concise methodology explanation."""

        st.subheader("Methodology")

        st.markdown(
            """
            This project builds a text-based risk signal from SEC filings.

            **Pipeline:**

            1. Pull recent 10-K and 10-Q filings from SEC EDGAR.
            2. Extract the Item 1A / Risk Factors section.
            3. Compare the current risk section against a previous filing.
            4. Generate NLP features such as TF-IDF change, word-count change, negative-term change, and uncertainty-term change.
            5. Combine those features into a bounded risk-change score.
            6. Run an event study around the filing date using post-filing returns, realized volatility, benchmark returns, and abnormal returns.
            7. Summarize whether higher risk-change filings show different market outcomes.

            **Important limitation:**

            The score is not a trading signal by itself. It is a research signal that needs broader validation across more companies, longer time periods, and stricter controls.
            """
        )

    @staticmethod
    def _parse_tickers(raw_text: str) -> list[str]:
        """Parse ticker text separated by spaces, commas, or new lines."""

        normalized = raw_text.replace(",", " ").replace("\n", " ")
        tickers = [
            token.upper().strip()
            for token in normalized.split(" ")
            if token.strip()
        ]

        return list(dict.fromkeys(tickers))

    @staticmethod
    def _display_dataframe_with_download(df: pd.DataFrame, file_name: str) -> None:
        """Display a DataFrame and provide a CSV download button."""

        if df.empty:
            st.warning("No rows returned.")
            return

        st.dataframe(df, use_container_width=True)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=file_name,
            mime="text/csv",
        )

    @st.cache_data(show_spinner=False)
    def _get_metadata(_self, ticker: str, limit: int) -> pd.DataFrame:
        """Cached filing metadata query."""

        return _self.pipeline.get_filing_metadata(ticker=ticker, limit=limit)

    @st.cache_data(show_spinner=False)
    def _get_scores(
        _self,
        ticker: str,
        limit: int,
        compare_mode: str,
    ) -> pd.DataFrame:
        """Cached risk-score query."""

        return _self.pipeline.build_risk_change_scores_df(
            ticker=ticker,
            limit=limit,
            compare_mode=compare_mode,
        )

    @st.cache_data(show_spinner=False)
    def _get_event_study(
        _self,
        ticker: str,
        limit: int,
        compare_mode: str,
        benchmark: str,
    ) -> pd.DataFrame:
        """Cached event-study query."""

        return _self.pipeline.build_event_study_df(
            ticker=ticker,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark,
        )

    @st.cache_data(show_spinner=False)
    def _get_summary(
        _self,
        ticker: str,
        limit: int,
        compare_mode: str,
        benchmark: str,
    ) -> pd.DataFrame:
        """Cached research-summary query."""

        return _self.pipeline.build_research_summary_df(
            ticker=ticker,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark,
        )

    @staticmethod
    def _prepare_date_chart_df(
        df: pd.DataFrame,
        date_column: str,
        value_column: str,
    ) -> pd.DataFrame:
        """Prepare a clean date/value DataFrame for Streamlit charts."""

        if df.empty or date_column not in df.columns or value_column not in df.columns:
            return pd.DataFrame()

        chart_df = df[[date_column, value_column]].copy()
        chart_df[date_column] = pd.to_datetime(chart_df[date_column], errors="coerce")
        chart_df = chart_df.dropna(subset=[date_column, value_column])
        chart_df = chart_df.sort_values(date_column)

        return chart_df


if __name__ == "__main__":
    RiskDashboardApp().run()