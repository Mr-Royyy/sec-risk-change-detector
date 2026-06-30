# SEC Risk Change Detector

A portfolio-grade quantitative finance + NLP project that detects changes in corporate risk disclosures from SEC filings.

## Current milestone

This starter version supports:

- Ticker to CIK lookup using SEC ticker mappings
- Recent 10-K / 10-Q filing metadata retrieval
- Direct filing URL construction
- Filing HTML download with local caching
- Item 1A / Risk Factors extraction
- CLI output to terminal or CSV
- OOP-based structure with documented classes and tests

## Why this project exists

The core research question is:

> When a company meaningfully changes its risk-disclosure language, does future volatility or abnormal return behavior change?

This first milestone builds the data foundation required before adding NLP features, event studies, ML models, and a dashboard.

## Project structure

```text
sec-risk-change-detector/
├── src/sec_risk_detector/
│   ├── __init__.py
│   ├── cache.py
│   ├── cli.py
│   ├── config.py
│   ├── exceptions.py
│   ├── models.py
│   ├── pipeline.py
│   ├── rate_limiter.py
│   ├── sec_client.py
│   ├── section_extractor.py
│   └── text_cleaner.py
├── tests/
│   ├── test_cache.py
│   ├── test_models.py
│   └── test_section_extractor.py
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── reports/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Setup

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows PowerShell
```

Install dependencies:

```bash
pip install -e .[dev]
```

Create your local environment file:

```bash
cp .env.example .env
```

Then edit `.env` and set a real SEC User-Agent:

```bash
SEC_USER_AGENT="Your Name your.email@example.com"
CACHE_DIR="data/raw/cache"
```

## Usage

Get recent filing metadata:

```bash
sec-risk AAPL --limit 5
```

Or with Python module syntax:

```bash
python -m sec_risk_detector.cli AAPL --limit 5
```

Extract risk sections and save to CSV:

```bash
sec-risk AAPL --limit 3 --extract-risk --output data/interim/aapl_risk_sections.csv
```

## Testing

```bash
pytest -q
```

## Current limitations

- Risk-section extraction is regex-based and will not be perfect for every filing format.
- The project currently supports metadata and risk-text extraction only.
- NLP feature engineering, event studies, market data, and model training are the next milestones.

## Next planned modules

1. `nlp_features.py` — TF-IDF similarity, embedding similarity, sentiment/uncertainty features.
2. `market_data.py` — post-filing price returns and realized volatility.
3. `event_study.py` — event windows and abnormal-return calculations.
4. `model.py` — predict post-filing volatility increase with time-aware validation.
5. `app/streamlit_app.py` — deployed dashboard.
