"""Streamlit dashboard for the SEC Risk Change Detector.

This dashboard provides an interactive portfolio-facing interface for the core
pipeline:
1. SEC filing metadata
2. Risk-factor extraction
3. NLP risk-change scoring
4. Event-study market reaction analysis
5. Research summary tables
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from sec_risk_detector.pipeline import FilingIngestionPipeline


class RiskDashboardApp:
    """Interactive dashboard for SEC filing risk-change analysis."""

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
            "Analyze changes in SEC risk-factor language and connect them to "
            "post-filing returns, volatility, and abnormal returns."
        )

        ticker, limit, compare_mode, benchmark = self._sidebar_controls()

        tab_metadata, tab_scores, tab_event_study, tab_summary, tab_top_events = st.tabs(
            [
                "Filing Metadata",
                "Risk Scores",
                "Event Study",
                "Summary",
                "Top Events",
            ]
        )

        with tab_metadata:
            self._render_metadata_tab(ticker=ticker, limit=limit)

        with tab_scores:
            self._render_scores_tab(
                ticker=ticker,
                limit=limit,
                compare_mode=compare_mode,
            )

        with tab_event_study:
            self._render_event_study_tab(
                ticker=ticker,
                limit=limit,
                compare_mode=compare_mode,
                benchmark=benchmark,
            )

        with tab_summary:
            self._render_summary_tab(
                ticker=ticker,
                limit=limit,
                compare_mode=compare_mode,
                benchmark=benchmark,
            )

        with tab_top_events:
            self._render_top_events_tab(
                ticker=ticker,
                limit=limit,
                compare_mode=compare_mode,
                benchmark=benchmark,
            )

    def _sidebar_controls(self) -> tuple[str, int, str, str]:
        """Render sidebar controls and return selected values."""

        st.sidebar.header("Controls")

        ticker = st.sidebar.text_input(
            "Ticker",
            value="AAPL",
            help="Enter a public company ticker such as AAPL, MSFT, TSLA, or NVDA.",
        ).upper().strip()

        limit = st.sidebar.slider(
            "Number of filings",
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
                "previous compares to the immediately prior filing."
            ),
        )

        benchmark = st.sidebar.text_input(
            "Benchmark",
            value="^GSPC",
            help="Benchmark ticker used for abnormal returns.",
        ).strip()

        st.sidebar.info(
            "For cleaner research results, use same-form comparison. "
            "It avoids comparing long 10-K risk sections directly against shorter 10-Q sections."
        )

        return ticker, limit, compare_mode, benchmark

    def _render_metadata_tab(self, ticker: str, limit: int) -> None:
        """Render recent SEC filing metadata."""

        st.subheader("Recent SEC Filings")

        if st.button("Load Filing Metadata", key="metadata_button"):
            with st.spinner("Fetching SEC filing metadata..."):
                df = self._get_metadata(ticker, limit)

            st.dataframe(df, use_container_width=True)

    def _render_scores_tab(self, ticker: str, limit: int, compare_mode: str) -> None:
        """Render NLP risk-change scores."""

        st.subheader("Risk Change Scores")

        if st.button("Calculate Risk Scores", key="scores_button"):
            with st.spinner("Extracting risk sections and calculating scores..."):
                df = self._get_scores(ticker, limit, compare_mode)

            st.dataframe(df, use_container_width=True)

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

    def _render_event_study_tab(
        self,
        ticker: str,
        limit: int,
        compare_mode: str,
        benchmark: str,
    ) -> None:
        """Render event-study results."""

        st.subheader("Post-Filing Market Reaction")

        if st.button("Run Event Study", key="event_button"):
            with st.spinner("Running event study..."):
                df = self._get_event_study(ticker, limit, compare_mode, benchmark)

            st.dataframe(df, use_container_width=True)

            chart_columns = [
                column
                for column in [
                    "final_risk_change_score",
                    "post_return_20d",
                    "abnormal_return_20d",
                    "post_vol_20d",
                ]
                if column in df.columns
            ]

            if chart_columns:
                st.write("Selected event-study metrics:")
                st.dataframe(
                    df[
                        [
                            "ticker",
                            "current_filing_date",
                            "current_form_type",
                            *chart_columns,
                        ]
                    ],
                    use_container_width=True,
                )

    def _render_summary_tab(
        self,
        ticker: str,
        limit: int,
        compare_mode: str,
        benchmark: str,
    ) -> None:
        """Render research summary by risk-score bucket."""

        st.subheader("Research Summary by Risk Score Bucket")

        if st.button("Build Summary", key="summary_button"):
            with st.spinner("Building research summary..."):
                df = self._get_summary(ticker, limit, compare_mode, benchmark)

            st.dataframe(df, use_container_width=True)

            if "avg_post_vol_20d" in df.columns:
                st.bar_chart(df, x="risk_score_bucket", y="avg_post_vol_20d")

            if "avg_abnormal_return_20d" in df.columns:
                st.bar_chart(df, x="risk_score_bucket", y="avg_abnormal_return_20d")

            st.caption(
                "Interpret this carefully for small samples. A single company with a small "
                "number of filings is useful for pipeline validation, not final statistical evidence."
            )

    def _render_top_events_tab(
        self,
        ticker: str,
        limit: int,
        compare_mode: str,
        benchmark: str,
    ) -> None:
        """Render highest risk-change filing events."""

        st.subheader("Top Risk-Change Events")

        top_n = st.slider(
            "Number of top events",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
        )

        if st.button("Find Top Events", key="top_events_button"):
            with st.spinner("Finding top risk-change events..."):
                df = self.pipeline.build_top_risk_events_df(
                    ticker=ticker,
                    limit=limit,
                    compare_mode=compare_mode,
                    benchmark_ticker=benchmark,
                    n=top_n,
                )

            st.dataframe(df, use_container_width=True)

    @st.cache_data(show_spinner=False)
    def _get_metadata(_self, ticker: str, limit: int) -> pd.DataFrame:
        """Cached filing metadata query."""

        return _self.pipeline.get_filing_metadata(ticker=ticker, limit=limit)

    @st.cache_data(show_spinner=False)
    def _get_scores(_self, ticker: str, limit: int, compare_mode: str) -> pd.DataFrame:
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