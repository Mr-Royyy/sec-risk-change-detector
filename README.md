# SEC Risk Change Detector

An institutional-style SEC risk research terminal that analyzes changes in company risk disclosures and tests whether those disclosure changes line up with post-filing market behavior.

The project combines SEC filing ingestion, NLP-based risk-change scoring, and event-study analysis into a Streamlit dashboard built for quantitative finance, financial data science, and investment research portfolio use.

## Live Demo

Launch the app: **[PASTE_YOUR_STREAMLIT_LINK_HERE](https://sec-risk-change-detector-zgqrfhtup9h6qzd6iwc3ga.streamlit.app/)**

## What This Project Does

Public companies disclose business risks in SEC filings such as 10-Ks and 10-Qs. These risk sections are often long, repetitive, and difficult to compare manually.

This project helps answer one research question:

> When a company materially changes its risk-factor language, does the market behave differently after the filing?

The system extracts SEC risk-factor sections, compares them against prior filings, creates an interpretable NLP risk-change score, and then tests post-filing returns, volatility, benchmark returns, and abnormal returns.

This is not presented as a trading signal. It is a research tool for studying whether disclosure-language changes have measurable market relevance.

## Key Features

- Pulls recent 10-K and 10-Q filings from SEC EDGAR
- Downloads and parses SEC filing HTML documents
- Extracts Item 1A / Risk Factors sections
- Compares risk disclosures across filings
- Supports same-form comparison, such as 10-Q to prior 10-Q
- Computes interpretable NLP risk-change features
- Calculates post-filing returns and realized volatility
- Calculates benchmark-adjusted abnormal returns
- Groups events into low, medium, and high risk-change buckets
- Supports single-ticker and multi-ticker batch analysis
- Provides an interactive Streamlit research dashboard
- Provides CSV downloads for further analysis
- Includes automated tests with pytest
- Includes GitHub Actions CI workflow

## Demo Walkthrough

A simple demo run:

1. Open the deployed app.
2. Keep the default ticker as `AAPL`.
3. Set filings per ticker to `3` or `5` for a fast public demo.
4. Keep comparison mode as `same-form`.
5. Keep benchmark as `^GSPC`.
6. Run `Risk Signal` to inspect SEC disclosure-language changes.
7. Run `Market Reaction` to connect those changes to returns, volatility, and abnormal returns.
8. Run `Research Summary` to view low, medium, and high risk-change buckets.
9. Download CSV outputs for further review.

For batch mode, try:

```text
AAPL MSFT NVDA
```

with `3` filings per ticker.

## Methodology

The pipeline has five main stages.

### 1. SEC Filing Ingestion

The user enters a ticker such as `AAPL`, `MSFT`, or `NVDA`.

The system maps the ticker to a company CIK, pulls recent 10-K and 10-Q filing metadata, and constructs the filing URLs needed for extraction.

### 2. Risk Section Extraction

The filing HTML is downloaded and cleaned.

The system extracts the Item 1A / Risk Factors section and stores the extracted text with metadata such as ticker, filing date, form type, accession number, filing URL, and word count.

### 3. NLP Risk-Change Scoring

Each filing is compared against a previous filing.

The project supports two comparison modes:

- `previous`: compare against the immediately previous filing
- `same-form`: compare 10-Q to previous 10-Q and 10-K to previous 10-K

The risk-change score uses interpretable NLP features:

- TF-IDF cosine similarity
- TF-IDF change score
- Word-count percentage change
- Negative-term frequency change
- Uncertainty-term frequency change
- Top added and removed terms

The goal is interpretability. The score is designed to help inspect disclosure changes, not to act as a black-box prediction model.

### 4. Event Study

For each filing event, the system calculates post-filing market behavior.

The event-study output includes:

- Post-filing returns over multiple windows
- Post-filing realized volatility
- Pre-filing realized volatility
- Benchmark returns
- Abnormal returns versus a benchmark such as the S&P 500

### 5. Research Summary

The event-study results are grouped into low, medium, and high risk-change buckets.

This helps test whether filings with higher disclosure-language change show different average market outcomes.

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
```

## Setup

Clone the repository:

```bash
git clone https://github.com/Mr-Royyy/sec-risk-change-detector.git
cd sec-risk-change-detector
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

On Windows PowerShell:

```powershell
.venv\Scripts\activate
```

Install the project:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create a local environment file:

```bash
copy .env.example .env
```

Set your SEC user agent in `.env`:

```env
SEC_USER_AGENT="Your Name your.email@example.com"
CACHE_DIR="data/raw/cache"
```

The SEC requests a descriptive user agent when accessing EDGAR data.

## CLI Usage

Fetch recent filing metadata:

```bash
python -m sec_risk_detector.cli AAPL --limit 5
```

Extract risk-factor sections:

```bash
python -m sec_risk_detector.cli AAPL --limit 5 --extract-risk
```

Calculate risk-change scores:

```bash
python -m sec_risk_detector.cli AAPL --limit 8 --score-risk --compare-mode same-form
```

Run event-study analysis:

```bash
python -m sec_risk_detector.cli AAPL --limit 8 --event-study --compare-mode same-form
```

Build a research summary:

```bash
python -m sec_risk_detector.cli AAPL --limit 8 --summary --compare-mode same-form
```

Show top risk-change events:

```bash
python -m sec_risk_detector.cli AAPL --limit 8 --top-events --compare-mode same-form --top-n 5
```

Run a multi-ticker batch summary:

```bash
python -m sec_risk_detector.cli --tickers AAPL MSFT NVDA TSLA JPM --limit 8 --summary --compare-mode same-form
```

Save output to CSV:

```bash
python -m sec_risk_detector.cli AAPL --limit 8 --event-study --compare-mode same-form --output data/processed/aapl_event_study.csv
```

## Streamlit Dashboard

Run the dashboard locally:

```bash
streamlit run app/streamlit_app.py
```

The dashboard supports:

- Single-ticker analysis
- Batch-universe analysis
- Risk-signal scoring
- Market-reaction analysis
- Research-summary tables
- Top risk-change event review
- CSV downloads

## Testing

Run the full test suite:

```bash
pytest
```

The project includes tests for:

- SEC filing models
- Disk caching
- Risk-section extraction
- NLP feature generation
- Event-study analysis
- Research-summary generation
- Multi-ticker batch pipeline logic

## Example Interpretation

A typical research summary groups filings into low, medium, and high risk-change buckets.

Example interpretation:

> In this sample, high risk-change filings showed different average 20-day abnormal returns and volatility than low risk-change filings. Because the sample is small, this should be treated as exploratory evidence rather than a trading conclusion.

This framing is intentional. The project is designed to show research discipline, not overclaim predictive power.

## Limitations

- SEC filing formats vary across companies and time.
- Risk-section extraction may require company-specific handling.
- Small sample sizes are not enough for strong statistical conclusions.
- yfinance is useful for research prototypes but is not institutional-grade market data.
- The current NLP score is interpretable but simple.
- The event study does not yet control for sector, earnings dates, macro events, or factor exposures.
- Public deployment may occasionally be affected by external API availability or rate limits.

## Future Improvements

Potential next steps:

- Add sentence-transformer embeddings for semantic disclosure change
- Add sector-level and market-factor controls
- Add earnings-date filters
- Add confidence intervals for bucket summaries
- Add regression testing across a larger universe
- Add persistent database storage with SQLite or PostgreSQL
- Add more robust extraction for unusual SEC filing formats
- Add scheduled batch runs for predefined universes
- Add report export to PDF or HTML

## Portfolio Summary

This project demonstrates:

- Financial data engineering
- SEC EDGAR ingestion
- NLP feature engineering
- Event-study methodology
- Batch research pipeline design
- Object-oriented Python structure
- CLI development
- Streamlit dashboard development
- Automated testing
- GitHub-based deployment workflow

The goal is to show how text-based financial disclosures can be converted into structured research signals and tested against observable market outcomes.
