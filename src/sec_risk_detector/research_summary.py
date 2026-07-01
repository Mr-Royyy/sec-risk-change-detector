"""Research summary tools for SEC risk-change event studies.

This module turns row-level event-study results into cleaner research tables.
The goal is to make the project easier to explain in a README, dashboard, or
interview.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ResearchSummaryConfig:
    """Configuration for research summary generation."""

    score_column: str = "final_risk_change_score"
    bucket_column: str = "risk_score_bucket"
    buckets: tuple[str, str, str] = ("low", "medium", "high")


class ResearchSummaryAnalyzer:
    """Create summary tables from event-study results."""

    def __init__(self, config: ResearchSummaryConfig | None = None) -> None:
        """Initialize summary analyzer."""

        self.config = config or ResearchSummaryConfig()

    def summarize(self, event_study_df: pd.DataFrame) -> pd.DataFrame:
        """Summarize event-study outcomes by risk-score bucket.

        Args:
            event_study_df: DataFrame returned by EventStudyAnalyzer.

        Returns:
            A DataFrame grouped by risk-score bucket.
        """

        required_columns = {
            self.config.score_column,
            "post_return_5d",
            "post_return_20d",
            "post_vol_5d",
            "post_vol_20d",
            "abnormal_return_5d",
            "abnormal_return_20d",
        }
        missing_columns = required_columns - set(event_study_df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        if event_study_df.empty:
            return pd.DataFrame()

        working_df = event_study_df.copy()
        working_df[self.config.bucket_column] = self._assign_score_buckets(
            working_df[self.config.score_column]
        )

        summary = (
            working_df.groupby(self.config.bucket_column, observed=True)
            .agg(
                filing_count=(self.config.score_column, "count"),
                avg_risk_change_score=(self.config.score_column, "mean"),
                avg_post_return_5d=("post_return_5d", "mean"),
                avg_post_return_20d=("post_return_20d", "mean"),
                avg_abnormal_return_5d=("abnormal_return_5d", "mean"),
                avg_abnormal_return_20d=("abnormal_return_20d", "mean"),
                avg_post_vol_5d=("post_vol_5d", "mean"),
                avg_post_vol_20d=("post_vol_20d", "mean"),
                median_post_vol_20d=("post_vol_20d", "median"),
            )
            .reset_index()
        )

        return summary

    def top_risk_events(
        self,
        event_study_df: pd.DataFrame,
        n: int = 10,
    ) -> pd.DataFrame:
        """Return the highest risk-change filing events.

        Args:
            event_study_df: DataFrame returned by EventStudyAnalyzer.
            n: Number of rows to return.

        Returns:
            DataFrame of top risk-change events.
        """

        required_columns = {
            "ticker",
            "current_filing_date",
            "current_form_type",
            self.config.score_column,
        }
        missing_columns = required_columns - set(event_study_df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        useful_columns = [
            column
            for column in [
                "ticker",
                "current_filing_date",
                "current_form_type",
                "previous_filing_date",
                "previous_form_type",
                self.config.score_column,
                "tfidf_change_score",
                "word_count_pct_change",
                "post_return_5d",
                "post_return_20d",
                "abnormal_return_5d",
                "abnormal_return_20d",
                "post_vol_5d",
                "post_vol_20d",
                "top_added_terms",
            ]
            if column in event_study_df.columns
        ]

        return (
            event_study_df.sort_values(self.config.score_column, ascending=False)
            .loc[:, useful_columns]
            .head(n)
            .reset_index(drop=True)
        )

    def _assign_score_buckets(self, scores: pd.Series) -> pd.Series:
        """Assign low/medium/high buckets using quantiles.

        For small samples or duplicate scores, qcut can fail. In that case, this
        method falls back to a simple rank-based bucket assignment.
        """

        clean_scores = pd.to_numeric(scores, errors="coerce")

        try:
            return pd.qcut(
                clean_scores,
                q=3,
                labels=list(self.config.buckets),
                duplicates="drop",
            )
        except ValueError:
            ranks = clean_scores.rank(method="first", pct=True)

            return pd.cut(
                ranks,
                bins=[0.0, 1 / 3, 2 / 3, 1.0],
                labels=list(self.config.buckets),
                include_lowest=True,
            )