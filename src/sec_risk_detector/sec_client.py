"""SEC API and filing download client.

The `SecClient` class owns all communication with SEC endpoints. Keeping this
logic in one object reduces duplicate request code and makes later testing much
easier.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable

import requests

from sec_risk_detector.cache import DiskCache
from sec_risk_detector.config import ProjectConfig
from sec_risk_detector.exceptions import CompanyNotFoundError, FilingDownloadError, SecApiError
from sec_risk_detector.models import Company, Filing
from sec_risk_detector.rate_limiter import RateLimiter


class SecClient:
    """Client for SEC ticker mapping, submissions API, and filing documents.

    Args:
        config: Project configuration with User-Agent, cache path, and timeout.
        cache: Optional cache dependency. Defaults to a DiskCache.
        rate_limiter: Optional rate limiter dependency. Defaults to a conservative limiter.
    """

    TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
    SUBMISSIONS_URL_TEMPLATE = "https://data.sec.gov/submissions/CIK{cik}.json"

    def __init__(
        self,
        config: ProjectConfig,
        cache: DiskCache | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self.config = config
        self.cache = cache or DiskCache(config.cache_dir)
        self.rate_limiter = rate_limiter or RateLimiter(config.max_requests_per_second)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": config.sec_user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov",
            }
        )

    def _headers_for_url(self, url: str) -> dict[str, str]:
        """Return headers adjusted for SEC host-specific requirements."""

        host = "data.sec.gov" if "data.sec.gov" in url else "www.sec.gov"
        return {
            "User-Agent": self.config.sec_user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": host,
        }

    def get_json(self, url: str, use_cache: bool = True) -> dict[str, Any] | list[Any]:
        """Fetch JSON from a URL with caching and rate limiting.

        Args:
            url: Endpoint URL.
            use_cache: Whether to read/write the disk cache.

        Raises:
            SecApiError: If the HTTP request or JSON parsing fails.
        """

        if use_cache:
            cached = self.cache.get_json(url)
            if cached is not None:
                return cached

        self.rate_limiter.wait()
        response = self.session.get(
            url,
            headers=self._headers_for_url(url),
            timeout=self.config.request_timeout,
        )
        if response.status_code != 200:
            raise SecApiError(f"SEC request failed: {response.status_code} for {url}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise SecApiError(f"Response was not valid JSON for {url}") from exc

        if use_cache:
            self.cache.set_json(url, payload)
        return payload

    def get_text(self, url: str, use_cache: bool = True) -> str:
        """Fetch text or HTML from a URL with caching and rate limiting.

        Args:
            url: Filing document URL.
            use_cache: Whether to read/write the disk cache.

        Raises:
            FilingDownloadError: If the filing cannot be downloaded.
        """

        if use_cache:
            cached = self.cache.get_text(url)
            if cached is not None:
                return cached

        self.rate_limiter.wait()
        response = self.session.get(
            url,
            headers=self._headers_for_url(url),
            timeout=self.config.request_timeout,
        )
        if response.status_code != 200:
            raise FilingDownloadError(f"Filing download failed: {response.status_code} for {url}")

        text = response.text
        if use_cache:
            self.cache.set_text(url, text)
        return text

    def get_ticker_map(self, use_cache: bool = True) -> dict[str, Company]:
        """Return a ticker-to-company mapping from SEC ticker data."""

        raw = self.get_json(self.TICKER_MAP_URL, use_cache=use_cache)
        if not isinstance(raw, dict):
            raise SecApiError("Unexpected ticker map payload format.")

        companies: dict[str, Company] = {}
        for entry in raw.values():
            ticker = str(entry["ticker"]).upper()
            cik = str(entry["cik_str"]).zfill(10)
            title = str(entry["title"])
            companies[ticker] = Company(ticker=ticker, cik=cik, name=title)
        return companies

    def lookup_company(self, ticker: str) -> Company:
        """Look up company metadata by ticker.

        Raises:
            CompanyNotFoundError: If ticker is missing from the SEC ticker map.
        """

        normalized = ticker.strip().upper()
        company = self.get_ticker_map().get(normalized)
        if company is None:
            raise CompanyNotFoundError(f"Ticker not found in SEC ticker map: {normalized}")
        return company

    def get_company_submissions(self, company: Company) -> dict[str, Any]:
        """Fetch the SEC submissions JSON for a company."""

        url = self.SUBMISSIONS_URL_TEMPLATE.format(cik=company.cik)
        payload = self.get_json(url)
        if not isinstance(payload, dict):
            raise SecApiError(f"Unexpected submissions payload for {company.ticker}")
        return payload

    def get_recent_filings(
        self,
        ticker: str,
        forms: Iterable[str] = ("10-K", "10-Q"),
        limit: int = 10,
    ) -> list[Filing]:
        """Return recent filings for a ticker, filtered by form type.

        Args:
            ticker: Stock ticker to look up.
            forms: Filing form types to keep.
            limit: Maximum number of filings to return after filtering.
        """

        company = self.lookup_company(ticker)
        payload = self.get_company_submissions(company)
        recent = payload.get("filings", {}).get("recent", {})
        if not recent:
            return []

        wanted_forms = {form.upper() for form in forms}
        filings: list[Filing] = []

        for i, form_type in enumerate(recent.get("form", [])):
            if str(form_type).upper() not in wanted_forms:
                continue

            filing_date = self._parse_date(recent["filingDate"][i])
            report_date = self._parse_optional_date(recent.get("reportDate", [None])[i])

            filing = Filing(
                company=company,
                form_type=str(form_type),
                filing_date=filing_date,
                report_date=report_date,
                accession_number=str(recent["accessionNumber"][i]),
                primary_document=str(recent["primaryDocument"][i]),
            )
            filings.append(filing)

            if len(filings) >= limit:
                break

        return filings

    @staticmethod
    def _parse_date(value: str) -> date:
        """Parse an SEC date string in YYYY-MM-DD format."""

        return date.fromisoformat(value)

    @staticmethod
    def _parse_optional_date(value: str | None) -> date | None:
        """Parse an optional SEC date string."""

        if not value:
            return None
        return date.fromisoformat(value)
