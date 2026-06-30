"""NLP feature generation for SEC risk-factor sections.

This module compares a company's current risk-factor text against its previous
risk-factor text and produces interpretable change metrics. The first version
uses lightweight, explainable features before we add heavier embedding models.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Literal
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOMAIN_STOPWORDS: frozenset[str] = frozenset(
    {
        "company",
        "business",
        "businesses",
        "results",
        "operations",
        "financial",
        "condition",
        "risk",
        "risks",
        "factor",
        "factors",
        "include",
        "including",
        "could",
        "would",
        "also",
    }
)

NEGATIVE_TERMS: frozenset[str] = frozenset(
    {
        "adverse",
        "adversely",
        "breach",
        "claims",
        "crisis",
        "decline",
        "delay",
        "disruption",
        "fail",
        "failed",
        "failure",
        "impairment",
        "loss",
        "losses",
        "penalty",
        "pressure",
        "reduce",
        "reduction",
        "shortage",
        "threat",
        "volatility",
        "weakness",
    }
)

UNCERTAINTY_TERMS: frozenset[str] = frozenset(
    {
        "contingent",
        "depend",
        "depends",
        "estimate",
        "estimated",
        "fluctuate",
        "fluctuations",
        "may",
        "might",
        "possible",
        "potential",
        "potentially",
        "uncertain",
        "uncertainties",
        "uncertainty",
        "unknown",
        "vary",
        "volatile",
        "volatility",
    }
)


@dataclass(frozen=True)
class RiskChangeMetrics:
    """Interpretable metrics comparing two risk-factor sections."""

    ticker: str
    current_filing_date: str
    previous_filing_date: str
    current_form_type: str
    previous_form_type: str
    current_accession_number: str
    previous_accession_number: str
    current_word_count: int
    previous_word_count: int
    word_count_pct_change: float
    tfidf_similarity: float
    tfidf_change_score: float
    negative_rate_change: float
    uncertainty_rate_change: float
    top_added_terms: str
    top_removed_terms: str
    final_risk_change_score: float

    def to_dict(self) -> dict[str, object]:
        """Return a DataFrame-friendly dictionary."""

        return asdict(self)


class RiskTextPreprocessor:
    """Prepare risk-factor text for lightweight NLP analysis."""

    def __init__(self, extra_stopwords: frozenset[str] = DOMAIN_STOPWORDS) -> None:
        self.stopwords = set(ENGLISH_STOP_WORDS) | set(extra_stopwords)

    def tokenize(self, text: str, remove_stopwords: bool = True) -> list[str]:
        """Tokenize text into lowercase words.

        Args:
            text: Raw or cleaned filing section text.
            remove_stopwords: Whether to remove English/domain stopwords.

        Returns:
            A list of lowercase tokens.
        """

        tokens = re.findall(r"[a-zA-Z][a-zA-Z\-']+", text.lower())
        if remove_stopwords:
            return [token for token in tokens if token not in self.stopwords and len(token) > 2]
        return [token for token in tokens if len(token) > 2]

    def count_terms(self, text: str) -> Counter[str]:
        """Return token counts after removing common noise words."""

        return Counter(self.tokenize(text, remove_stopwords=True))

    def term_rate_per_1000_words(self, text: str, terms: frozenset[str]) -> float:
        """Count target terms per 1,000 words using non-stopword-filtered tokens."""

        tokens = self.tokenize(text, remove_stopwords=False)
        if not tokens:
            return 0.0
        matches = sum(1 for token in tokens if token in terms)
        return matches / len(tokens) * 1000

class RiskChangeAnalyzer:
    """Create risk-change features from extracted filing sections."""

    def __init__(
        self,
        preprocessor: RiskTextPreprocessor | None = None,
        top_n_terms: int = 10,
    ) -> None:
        self.preprocessor = preprocessor or RiskTextPreprocessor()
        self.top_n_terms = top_n_terms

    def compare_rows(self, current_row: pd.Series, previous_row: pd.Series) -> RiskChangeMetrics:
        """Compare two extracted risk-section rows."""

        current_text = str(current_row.get("risk_text", "") or "")
        previous_text = str(previous_row.get("risk_text", "") or "")

        current_word_count = self._safe_int(current_row.get("risk_word_count"), current_text)
        previous_word_count = self._safe_int(previous_row.get("risk_word_count"), previous_text)

        word_count_pct_change = self._percent_change(current_word_count, previous_word_count)
        tfidf_similarity = self._tfidf_similarity(previous_text, current_text)
        tfidf_change_score = 1.0 - tfidf_similarity

        negative_rate_change = self._rate_change(current_text, previous_text, NEGATIVE_TERMS)
        uncertainty_rate_change = self._rate_change(current_text, previous_text, UNCERTAINTY_TERMS)
        added_terms, removed_terms = self._term_differences(current_text, previous_text)

        final_score = self._final_score(
            tfidf_change_score=tfidf_change_score,
            word_count_pct_change=word_count_pct_change,
            negative_rate_change=negative_rate_change,
            uncertainty_rate_change=uncertainty_rate_change,
        )

        return RiskChangeMetrics(
            ticker=str(current_row["ticker"]),
            current_filing_date=str(current_row["filing_date"]),
            previous_filing_date=str(previous_row["filing_date"]),
            current_form_type=str(current_row["form_type"]),
            previous_form_type=str(previous_row["form_type"]),
            current_accession_number=str(current_row["accession_number"]),
            previous_accession_number=str(previous_row["accession_number"]),
            current_word_count=current_word_count,
            previous_word_count=previous_word_count,
            word_count_pct_change=round(word_count_pct_change, 6),
            tfidf_similarity=round(tfidf_similarity, 6),
            tfidf_change_score=round(tfidf_change_score, 6),
            negative_rate_change=round(negative_rate_change, 6),
            uncertainty_rate_change=round(uncertainty_rate_change, 6),
            top_added_terms=", ".join(added_terms),
            top_removed_terms=", ".join(removed_terms),
            final_risk_change_score=round(final_score, 6),
        )

    def compare_dataframe(
        self,
        sections_df: pd.DataFrame,
        compare_mode: str = "previous",
    ) -> pd.DataFrame:
        """Compare risk sections using the selected comparison mode.

        Args:
            sections_df: DataFrame produced by the risk-section extraction pipeline.
            compare_mode: Either "previous" or "same-form".

        Returns:
            DataFrame of current-vs-previous risk-change metrics.
        """

        required_columns = {"ticker", "filing_date", "form_type", "risk_text", "risk_word_count"}
        missing_columns = required_columns - set(sections_df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        if compare_mode not in {"previous", "same-form"}:
            raise ValueError("compare_mode must be either 'previous' or 'same-form'.")

        clean_df = sections_df.copy()
        clean_df["filing_date"] = pd.to_datetime(clean_df["filing_date"])
        clean_df = clean_df.sort_values(["ticker", "filing_date"])

        if compare_mode == "previous":
            group_columns = ["ticker"]
        else:
            group_columns = ["ticker", "form_type"]

        results: list[RiskChangeMetrics] = []

        for _, group_df in clean_df.groupby(group_columns, sort=False):
            rows = list(group_df.iterrows())

            for index in range(1, len(rows)):
                previous_row = rows[index - 1][1]
                current_row = rows[index][1]
                results.append(self.compare_rows(current_row, previous_row))

        return pd.DataFrame([result.to_dict() for result in results])

    def _rate_change(
        self,
        current_text: str,
        previous_text: str,
        terms: frozenset[str],
    ) -> float:
        """Return current minus previous target-term rate per 1,000 words."""

        current_rate = self.preprocessor.term_rate_per_1000_words(current_text, terms)
        previous_rate = self.preprocessor.term_rate_per_1000_words(previous_text, terms)
        return current_rate - previous_rate

    def _tfidf_similarity(self, previous_text: str, current_text: str) -> float:
        """Return TF-IDF cosine similarity for two pieces of text."""

        if not previous_text.strip() or not current_text.strip():
            return 0.0

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([previous_text, current_text])
        similarity = cosine_similarity(matrix[0], matrix[1])[0][0]

        return float(max(0.0, min(1.0, similarity)))

    def _term_differences(self, current_text: str, previous_text: str) -> tuple[list[str], list[str]]:
        """Return terms that increased and decreased the most."""

        current_counts = self.preprocessor.count_terms(current_text)
        previous_counts = self.preprocessor.count_terms(previous_text)

        vocabulary = set(current_counts) | set(previous_counts)

        differences = {
            term: current_counts.get(term, 0) - previous_counts.get(term, 0)
            for term in vocabulary
        }

        added = [
            term
            for term, diff in sorted(
                differences.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            if diff > 0
        ]

        removed = [
            term
            for term, diff in sorted(
                differences.items(),
                key=lambda item: item[1],
            )
            if diff < 0
        ]

        return added[: self.top_n_terms], removed[: self.top_n_terms]

    @staticmethod
    def _safe_int(value: object, fallback_text: str) -> int:
        """Convert a value to int or use a text word-count fallback."""

        try:
            if value is not None and not (isinstance(value, float) and math.isnan(value)):
                return int(value)
        except (TypeError, ValueError):
            pass

        return len(str(fallback_text).split())

    @staticmethod
    def _percent_change(current_value: int, previous_value: int) -> float:
        """Return percent change while avoiding division by zero."""

        if previous_value == 0:
            return 0.0

        return (current_value - previous_value) / previous_value

    @staticmethod
    def _final_score(
        tfidf_change_score: float,
        word_count_pct_change: float,
        negative_rate_change: float,
        uncertainty_rate_change: float,
    ) -> float:
        """Combine metrics into a bounded 0-to-1 risk-change score."""

        length_component = min(abs(word_count_pct_change), 1.0)
        negative_component = min(max(negative_rate_change, 0.0) / 5.0, 1.0)
        uncertainty_component = min(max(uncertainty_rate_change, 0.0) / 5.0, 1.0)

        score = (
            0.50 * tfidf_change_score
            + 0.20 * length_component
            + 0.15 * negative_component
            + 0.15 * uncertainty_component
        )

        return max(0.0, min(1.0, score))
    """Create risk-change features from extracted filing sections."""

    def __init__(
        self,
        preprocessor: RiskTextPreprocessor | None = None,
        top_n_terms: int = 10,
    ) -> None:
        self.preprocessor = preprocessor or RiskTextPreprocessor()
        self.top_n_terms = top_n_terms

    def compare_rows(self, current_row: pd.Series, previous_row: pd.Series) -> RiskChangeMetrics:
        """Compare two extracted risk-section rows.

        Args:
            current_row: Newer filing row containing risk_text and metadata.
            previous_row: Older filing row containing risk_text and metadata.

        Returns:
            RiskChangeMetrics object with interpretable text-change signals.
        """

        current_text = str(current_row.get("risk_text", "") or "")
        previous_text = str(previous_row.get("risk_text", "") or "")

        current_word_count = self._safe_int(current_row.get("risk_word_count"), current_text)
        previous_word_count = self._safe_int(previous_row.get("risk_word_count"), previous_text)

        word_count_pct_change = self._percent_change(current_word_count, previous_word_count)
        tfidf_similarity = self._tfidf_similarity(previous_text, current_text)
        tfidf_change_score = 1.0 - tfidf_similarity

        negative_rate_change = self._rate_change(current_text, previous_text, NEGATIVE_TERMS)
        uncertainty_rate_change = self._rate_change(current_text, previous_text, UNCERTAINTY_TERMS)
        added_terms, removed_terms = self._term_differences(current_text, previous_text)

        final_score = self._final_score(
            tfidf_change_score=tfidf_change_score,
            word_count_pct_change=word_count_pct_change,
            negative_rate_change=negative_rate_change,
            uncertainty_rate_change=uncertainty_rate_change,
        )

        return RiskChangeMetrics(
            ticker=str(current_row["ticker"]),
            current_filing_date=str(current_row["filing_date"]),
            previous_filing_date=str(previous_row["filing_date"]),
            current_form_type=str(current_row["form_type"]),
            previous_form_type=str(previous_row["form_type"]),
            current_accession_number=str(current_row["accession_number"]),
            previous_accession_number=str(previous_row["accession_number"]),
            current_word_count=current_word_count,
            previous_word_count=previous_word_count,
            word_count_pct_change=round(word_count_pct_change, 6),
            tfidf_similarity=round(tfidf_similarity, 6),
            tfidf_change_score=round(tfidf_change_score, 6),
            negative_rate_change=round(negative_rate_change, 6),
            uncertainty_rate_change=round(uncertainty_rate_change, 6),
            top_added_terms=", ".join(added_terms),
            top_removed_terms=", ".join(removed_terms),
            final_risk_change_score=round(final_score, 6),
        )

        def compare_dataframe(
            self,
            sections_df: pd.DataFrame,
            compare_mode: Literal["previous", "same-form"] = "previous",
        ) -> pd.DataFrame:
            """Compare risk sections using the selected comparison mode.

            Args:
                sections_df: DataFrame produced by the risk-section extraction pipeline.
                compare_mode: Comparison method.

                    "previous":
                        Compare each filing to the immediately previous filing for
                        the same ticker, regardless of form type.

                    "same-form":
                        Compare each filing to the immediately previous filing with
                        the same ticker and same form type. This avoids comparing
                        10-K filings directly against 10-Q filings.

            Returns:
                A DataFrame of current-vs-previous risk-change metrics.
            """

            required_columns = {"ticker", "filing_date", "form_type", "risk_text", "risk_word_count"}
            missing_columns = required_columns - set(sections_df.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

            if compare_mode not in {"previous", "same-form"}:
                raise ValueError(
                    "compare_mode must be either 'previous' or 'same-form'."
                )

            clean_df = sections_df.copy()
            clean_df["filing_date"] = pd.to_datetime(clean_df["filing_date"])
            clean_df = clean_df.sort_values(["ticker", "filing_date"])

            if compare_mode == "previous":
                group_columns = ["ticker"]
            else:
                group_columns = ["ticker", "form_type"]

            results: list[RiskChangeMetrics] = []

            for _, group_df in clean_df.groupby(group_columns, sort=False):
                rows = list(group_df.iterrows())

                for index in range(1, len(rows)):
                    previous_row = rows[index - 1][1]
                    current_row = rows[index][1]
                    results.append(self.compare_rows(current_row, previous_row))

            return pd.DataFrame([result.to_dict() for result in results])

    def _rate_change(
        self,
        current_text: str,
        previous_text: str,
        terms: frozenset[str],
    ) -> float:
        """Return current minus previous target-term rate per 1,000 words."""

        current_rate = self.preprocessor.term_rate_per_1000_words(current_text, terms)
        previous_rate = self.preprocessor.term_rate_per_1000_words(previous_text, terms)
        return current_rate - previous_rate

    def _tfidf_similarity(self, previous_text: str, current_text: str) -> float:
        """Return TF-IDF cosine similarity for two pieces of text."""

        if not previous_text.strip() or not current_text.strip():
            return 0.0

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([previous_text, current_text])
        similarity = cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(max(0.0, min(1.0, similarity)))

    def _term_differences(self, current_text: str, previous_text: str) -> tuple[list[str], list[str]]:
        """Return terms that increased and decreased the most."""

        current_counts = self.preprocessor.count_terms(current_text)
        previous_counts = self.preprocessor.count_terms(previous_text)
        vocabulary = set(current_counts) | set(previous_counts)
        differences = {
            term: current_counts.get(term, 0) - previous_counts.get(term, 0)
            for term in vocabulary
        }
        added = [
            term
            for term, diff in sorted(
                differences.items(), key=lambda item: item[1], reverse=True
            )
            if diff > 0
        ]
        removed = [
            term
            for term, diff in sorted(differences.items(), key=lambda item: item[1])
            if diff < 0
        ]
        return added[: self.top_n_terms], removed[: self.top_n_terms]

    @staticmethod
    def _safe_int(value: object, fallback_text: str) -> int:
        """Convert a value to int or use a text word-count fallback."""

        try:
            if value is not None and not (isinstance(value, float) and math.isnan(value)):
                return int(value)
        except (TypeError, ValueError):
            pass
        return len(str(fallback_text).split())

    @staticmethod
    def _percent_change(current_value: int, previous_value: int) -> float:
        """Return percent change while avoiding division by zero."""

        if previous_value == 0:
            return 0.0
        return (current_value - previous_value) / previous_value

    @staticmethod
    def _final_score(
        tfidf_change_score: float,
        word_count_pct_change: float,
        negative_rate_change: float,
        uncertainty_rate_change: float,
    ) -> float:
        """Combine metrics into a bounded 0-to-1 risk-change score."""

        length_component = min(abs(word_count_pct_change), 1.0)
        negative_component = min(max(negative_rate_change, 0.0) / 5.0, 1.0)
        uncertainty_component = min(max(uncertainty_rate_change, 0.0) / 5.0, 1.0)
        score = (
            0.50 * tfidf_change_score
            + 0.20 * length_component
            + 0.15 * negative_component
            + 0.15 * uncertainty_component
        )
        return max(0.0, min(1.0, score))