"""SEC Risk Change Detector package.

This package ingests SEC filings, extracts risk-related text, and prepares
research datasets for NLP-driven risk disclosure analysis.
"""

from sec_risk_detector.models import Company, Filing

__all__ = ["Company", "Filing"]
