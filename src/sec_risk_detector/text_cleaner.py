"""Text cleaning utilities for SEC filings."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup


class FilingTextCleaner:
    """Convert SEC filing HTML into normalized plain text."""

    def html_to_text(self, html: str) -> str:
        """Convert HTML to readable text while preserving section boundaries.

        Args:
            html: Raw SEC filing HTML.

        Returns:
            Normalized plain text.
        """

        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        return self.normalize_whitespace(text)

    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace without removing all useful line breaks."""

        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        return text.strip()

    def collapse_for_modeling(self, text: str) -> str:
        """Collapse text into a single paragraph-style string for NLP features."""

        return re.sub(r"\s+", " ", text).strip()
