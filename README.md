# SEC Risk Change Detector

A Python-based quant finance and NLP project that analyzes changes in SEC risk-factor disclosures and tests whether those changes are associated with post-filing market outcomes such as returns, volatility, and abnormal returns.

This project is designed as a portfolio-ready research tool for quantitative finance, financial data science, and machine learning roles.

## Project Overview

Public companies disclose business risks in SEC filings such as 10-Ks and 10-Qs. This project extracts those risk-factor sections, compares them against previous filings, creates an NLP-based risk-change score, and then runs an event study around the filing date.

The core research question is:

> When a company materially changes its risk disclosure language, does the market show different post-filing behavior?

The project does not claim to produce a trading signal. Instead, it builds a research pipeline for studying whether text-based changes in corporate disclosures are related to future market volatility, returns, or abnormal returns.

## Features

- Pulls recent 10-K and 10-Q filing metadata from SEC EDGAR
- Downloads filing HTML documents
- Extracts Item 1A / Risk Factors sections
- Computes NLP-based risk-change metrics
- Supports same-form comparisons, such as 10-Q to prior 10-Q
- Calculates post-filing returns and realized volatility
- Calculates benchmark-adjusted abnormal returns
- Summarizes results by low, medium, and high risk-change buckets
- Supports single-ticker and multi-ticker batch analysis
- Includes an interactive Streamlit dashboard
- Includes automated tests with pytest
- Includes GitHub Actions CI workflow

## Methodology

The pipeline has five main stages:

1. **SEC Filing Ingestion**

   The user enters a ticker such as `AAPL`, `MSFT`, or `NVDA`. The system maps the ticker to a CIK, pulls recent 10-K and 10-Q filing metadata, and constructs filing URLs.

2. **Risk Section Extraction**

   The filing HTML is downloaded and cleaned. The system extracts the Item 1A / Risk Factors section and stores the extracted text with metadata such as filing date, form type, accession number, and word count.

3. **NLP Risk Change Scoring**

   Each filing is compared against a previous filing. The project supports two comparison modes:

   - `previous`: compare against the immediately previous filing
   - `same-form`: compare 10-Q to prior 10-Q and 10-K to prior 10-K

   The score uses interpretable NLP features:

   - TF-IDF cosine similarity
   - TF-IDF change score
   - Word-count percentage change
   - Negative-term frequency change
   - Uncertainty-term frequency change
   - Top added and removed risk terms

4. **Event Study**

   For each filing date, the system calculates:

   - Post-filing returns over 1, 5, 10, and 20 trading days
   - Post-filing realized volatility
   - Pre-filing 60-day realized volatility
   - Benchmark returns
   - Abnormal returns versus a benchmark such as the S&P 500

5. **Research Summary**

   The event-study results are grouped into low, medium, and high risk-change buckets to study whether higher risk-change filings are associated with different market outcomes.

## Tech Stack

- Python
- pandas
- NumPy
- scikit-learn
- BeautifulSoup
- lxml
- requests
- yfinance
- Streamlit
- pytest
- GitHub Actions

## Project Structure

```text
sec-risk-change-detector/
│
├── app/
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── reports/
│
├── src/
│   └── sec_risk_detector/
│       ├── cache.py
│       ├── cli.py
│       ├── config.py
│       ├── event_study.py
│       ├── market_data.py
│       ├── models.py
│       ├── nlp_features.py
│       ├── pipeline.py
│       ├── rate_limiter.py
│       ├── research_summary.py
│       ├── sec_client.py
│       ├── section_extractor.py
│       └── text_cleaner.py
│
├── tests/
├── .github/workflows/
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md