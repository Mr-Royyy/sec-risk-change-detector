"""Risk-factor section extraction for 10-K and 10-Q filings."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from sec_risk_detector.models import ExtractedSection, Filing
from sec_risk_detector.text_cleaner import FilingTextCleaner


@dataclass(frozen=True)
class SectionCandidate:
    """Candidate section span found by regex search."""

    start: int
    end: int
    text: str

    @property
    def length(self) -> int:
        """Return candidate character length."""

        return len(self.text)


class RiskSectionExtractor:
    """Extract Item 1A / Risk Factors text from filing HTML.

    SEC filings are not perfectly standardized, so this class finds multiple
    candidate spans and chooses the longest plausible one. This avoids many
    table-of-contents false positives where "Item 1A" appears only as a link.
    """

    START_PATTERNS = (
        re.compile(r"\bitem\s+1a\.?\s+risk\s+factors\b", re.IGNORECASE),
        re.compile(r"\brisk\s+factors\b", re.IGNORECASE),
    )

    END_PATTERN = re.compile(
        r"\bitem\s+(?:1b|2|3|7|8)\.?\s+|\bpart\s+ii\s+item\s+2\b|\bsignatures\b",
        re.IGNORECASE,
    )

    def __init__(self, cleaner: FilingTextCleaner | None = None) -> None:
        self.cleaner = cleaner or FilingTextCleaner()

    def extract_from_html(self, filing: Filing, html: str) -> ExtractedSection:
        """Extract risk-factor text from a filing's raw HTML.

        Args:
            filing: Filing metadata.
            html: Raw filing HTML.

        Returns:
            ExtractedSection with text and a simple quality flag.
        """

        plain_text = self.cleaner.html_to_text(html)
        section_text = self.extract_text(plain_text)
        word_count = self._count_words(section_text)
        quality = self._quality_flag(word_count, len(section_text))
        return ExtractedSection(
            filing=filing,
            section_name="Item 1A - Risk Factors",
            text=section_text,
            word_count=word_count,
            extraction_quality=quality,
        )

    def extract_text(self, plain_text: str) -> str:
        """Extract risk-factor text from normalized plain text.

        Args:
            plain_text: Text already converted from HTML.

        Returns:
            Best candidate section text, or an empty string if not found.
        """

        candidates = self._find_candidates(plain_text)
        if not candidates:
            return ""

        best = max(candidates, key=lambda candidate: candidate.length)
        return best.text.strip()

    def _find_candidates(self, text: str) -> list[SectionCandidate]:
        """Find plausible risk-factor section spans."""

        candidates: list[SectionCandidate] = []
        for start_match in self._iter_start_matches(text):
            start = start_match.start()
            end = self._find_section_end(text, start_match.end())
            section = text[start:end].strip()
            if section:
                candidates.append(SectionCandidate(start=start, end=end, text=section))
        return candidates

    def _iter_start_matches(self, text: str) -> Iterable[re.Match[str]]:
        """Yield start matches from all known risk-factor headings."""

        seen_starts: set[int] = set()
        for pattern in self.START_PATTERNS:
            for match in pattern.finditer(text):
                if match.start() not in seen_starts:
                    seen_starts.add(match.start())
                    yield match

    def _find_section_end(self, text: str, search_from: int) -> int:
        """Find the next likely SEC section heading after a start position."""

        match = self.END_PATTERN.search(text, search_from)
        return match.start() if match else len(text)

    @staticmethod
    def _count_words(text: str) -> int:
        """Count words in extracted text."""

        return len(re.findall(r"\b\w+\b", text))

    @staticmethod
    def _quality_flag(word_count: int, char_count: int) -> str:
        """Return a simple extraction quality label."""

        if word_count == 0:
            return "missing"
        if word_count < 250:
            return "short"
        if char_count > 500_000:
            return "suspiciously_long"
        return "good"
