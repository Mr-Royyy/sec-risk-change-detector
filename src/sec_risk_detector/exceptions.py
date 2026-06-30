"""Custom exceptions for the SEC Risk Change Detector project."""


class SecRiskDetectorError(Exception):
    """Base exception for project-specific errors."""


class SecApiError(SecRiskDetectorError):
    """Raised when a request to an SEC endpoint fails."""


class CompanyNotFoundError(SecRiskDetectorError):
    """Raised when a ticker cannot be mapped to a company/CIK."""


class FilingDownloadError(SecRiskDetectorError):
    """Raised when a filing document cannot be downloaded."""


class SectionExtractionError(SecRiskDetectorError):
    """Raised when a requested filing section cannot be extracted cleanly."""
