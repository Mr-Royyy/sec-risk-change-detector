"""Streamlit dashboard for the SEC Risk Change Detector.

This file only refactors the frontend experience. The backend pipeline and
analysis methods are unchanged.
"""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from sec_risk_detector.pipeline import FilingIngestionPipeline


DEFAULT_UNIVERSE = "AAPL MSFT NVDA TSLA JPM WMT XOM AMZN META NFLX"


class RiskDashboardApp:
    """Interactive dashboard for SEC risk-change analysis."""

    def __init__(self) -> None:
        """Initialize dashboard dependencies."""

        self.pipeline = FilingIngestionPipeline()

    def run(self) -> None:
        """Render the Streamlit app."""

        st.set_page_config(
            page_title="SEC Risk Change Detector",
            page_icon="■",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        self._inject_css()
        controls = self._sidebar_controls()

        st.markdown('<main class="page-shell">', unsafe_allow_html=True)
        self._render_hero(controls)
        self._render_result_preview()

        tabs = st.tabs(
            [
                "Overview",
                "Risk Signal",
                "Market Reaction",
                "Research Summary",
                "Top Events",
                "Methodology",
            ]
        )

        with tabs[0]:
            self._render_overview_tab(controls)

        with tabs[1]:
            self._render_risk_signal_tab(controls)

        with tabs[2]:
            self._render_market_reaction_tab(controls)

        with tabs[3]:
            self._render_summary_tab(controls)

        with tabs[4]:
            self._render_top_events_tab(controls)

        with tabs[5]:
            self._render_methodology_tab()

        st.markdown("</main>", unsafe_allow_html=True)

    def _inject_css(self) -> None:
        """Inject the editorial design system."""

        st.markdown(
            """

                        <style>
                @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700;800&display=swap');

                :root {
                    --background: #FAFAF8;
                    --paper: #FFFFFF;
                    --paper-soft: #F7F2EA;
                    --foreground: #151515;
                    --muted: #3F3A35;
                    --muted-2: #595149;
                    --accent: #A97705;
                    --accent-soft: #C89322;
                    --border: #D5CABD;
                    --border-strong: #B8AA98;
                    --success: #2F7D4E;
                    --success-soft: #EAF5EE;
                    --shadow-sm: 0 4px 14px rgba(26, 26, 26, 0.065);
                    --shadow-md: 0 14px 34px rgba(26, 26, 26, 0.095);
                    --shadow-lg: 0 28px 78px rgba(26, 26, 26, 0.135);
                    --radius-sm: 12px;
                    --radius-md: 18px;
                    --radius-lg: 28px;
                    --max: 1640px;
                    --sidebar: 340px;

                    --font-label: 1rem;
                    --font-body: 1.18rem;
                    --font-body-lg: 1.35rem;
                    --font-card-title: 1.75rem;
                    --font-section-title: 2.35rem;
                    --font-hero: clamp(3rem, 4.05vw, 3.55rem);
                }

                html, body, [class*="css"] {
                    font-family: "Source Sans 3", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: var(--foreground);
                    font-size: 18px;
                }

                .stApp {
                    background:
                        radial-gradient(circle at 8% 2%, rgba(169, 119, 5, 0.075), transparent 32rem),
                        radial-gradient(circle at 90% 5%, rgba(200, 147, 34, 0.07), transparent 32rem),
                        linear-gradient(180deg, #FAFAF8 0%, #F4EFE7 100%);
                    color: var(--foreground);
                }

                .stApp::before {
                    content: "";
                    position: fixed;
                    inset: 0;
                    pointer-events: none;
                    opacity: 0.18;
                    background-image: radial-gradient(rgba(26, 26, 26, 0.052) 0.55px, transparent 0.55px);
                    background-size: 5px 5px;
                    mix-blend-mode: multiply;
                    z-index: 0;
                }

                [data-testid="stHeader"] {
                    background: rgba(250, 250, 248, 0.88);
                    backdrop-filter: blur(14px);
                    border-bottom: 1px solid rgba(217, 209, 198, 0.82);
                }

                .block-container {
                    max-width: none !important;
                    width: 100% !important;
                    padding: 1.75rem 2.75rem 7rem 2.75rem !important;
                }

                .page-shell {
                    width: min(100%, var(--max));
                    max-width: var(--max);
                    margin: 0 auto;
                }

                /* Sidebar: make the setup controls readable and touch friendly. */
                section[data-testid="stSidebar"] {
                    width: var(--sidebar) !important;
                    min-width: var(--sidebar) !important;
                    background: linear-gradient(180deg, #F2EDE4 0%, #EEE7DC 100%);
                    border-right: 1px solid var(--border-strong);
                    box-shadow: 10px 0 32px rgba(26, 26, 26, 0.06);
                }

                section[data-testid="stSidebar"] > div {
                    width: var(--sidebar) !important;
                    min-width: var(--sidebar) !important;
                    padding-left: 1.65rem;
                    padding-right: 1.65rem;
                }

                [data-testid="stSidebar"] section {
                    padding-top: 1.75rem;
                }

                [data-testid="stSidebar"] * {
                    color: var(--foreground);
                }

                [data-testid="stSidebar"] h3 {
                    font-family: "Playfair Display", Georgia, serif;
                    font-size: 2.15rem;
                    font-weight: 650;
                    margin: 0 0 0.6rem 0;
                    letter-spacing: -0.02em;
                }

                [data-testid="stSidebar"] .stCaptionContainer,
                [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                    color: var(--muted) !important;
                    font-size: 1.05rem !important;
                    line-height: 1.55;
                    margin-bottom: 1.5rem;
                }

                [data-testid="stSidebar"] label {
                    font-family: "IBM Plex Mono", monospace;
                    color: var(--foreground) !important;
                    font-size: 1rem !important;
                    font-weight: 700 !important;
                    letter-spacing: 0.055em;
                    text-transform: uppercase;
                    line-height: 1.35 !important;
                    margin-bottom: 0.35rem !important;
                }

                [data-testid="stSidebar"] .stTextInput,
                [data-testid="stSidebar"] .stTextArea,
                [data-testid="stSidebar"] .stSelectbox,
                [data-testid="stSidebar"] .stRadio,
                [data-testid="stSidebar"] .stSlider {
                    margin-bottom: 1.95rem;
                    padding-bottom: 0.95rem;
                    border-bottom: 1px solid rgba(217, 209, 198, 0.68);
                }

                [data-testid="stSidebar"] input,
                [data-testid="stSidebar"] textarea,
                [data-testid="stSidebar"] select,
                [data-baseweb="select"] > div {
                    min-height: 56px !important;
                    font-size: 1.12rem !important;
                    border-radius: 12px !important;
                }

                [data-testid="stSidebar"] [role="radiogroup"] label,
                [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
                [data-testid="stSidebar"] [data-baseweb="slider"] {
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    font-size: 1.1rem !important;
                    font-weight: 650 !important;
                    letter-spacing: 0 !important;
                    text-transform: none !important;
                    line-height: 1.45 !important;
                }

                [data-testid="stSidebar"] .callout {
                    font-size: 1.08rem;
                    padding: 1.25rem 1.35rem;
                    line-height: 1.55;
                    border-radius: 16px;
                    border-left: 5px solid var(--accent);
                    background: rgba(255, 255, 255, 0.82);
                }

                h1, h2, h3, h4 {
                    font-family: "Playfair Display", Georgia, serif;
                    color: var(--foreground);
                    letter-spacing: -0.025em;
                }

                p, li, .stMarkdown, [data-testid="stMarkdownContainer"] {
                    color: var(--muted);
                    line-height: 1.7;
                    font-size: var(--font-body);
                }

                /* Top hero: intentionally taller and more readable. */
                .hero {
                    display: grid;
                    grid-template-columns: minmax(0, 7.6fr) minmax(360px, 4.4fr);
                    gap: 2.25rem;
                    align-items: stretch;
                    background: rgba(255, 255, 255, 0.74);
                    border: 1px solid var(--border-strong);
                    border-top: 5px solid var(--foreground);
                    border-radius: var(--radius-lg);
                    padding: 3.25rem;
                    margin: 0.65rem 0 2.75rem 0;
                    box-shadow: var(--shadow-md);
                }

                .hero-main {
                    min-height: 520px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }

                .label-row {
                    display: flex;
                    align-items: center;
                    gap: 1.15rem;
                    margin-bottom: 1.55rem;
                }

                .label-line {
                    width: 5.5rem;
                    height: 2px;
                    background: var(--accent);
                }

                .small-caps {
                    font-family: "IBM Plex Mono", monospace;
                    font-size: 1rem;
                    font-weight: 700;
                    letter-spacing: 0.075em;
                    text-transform: uppercase;
                    color: var(--accent);
                    line-height: 1.35;
                }

                .hero-title {
                    font-family: "Playfair Display", Georgia, serif;
                    font-size: var(--font-hero);
                    font-weight: 700;
                    line-height: 1.03;
                    letter-spacing: -0.045em;
                    margin: 0;
                    color: var(--foreground);
                    max-width: 980px;
                }

                .hero-title em {
                    color: var(--accent);
                    font-style: italic;
                    font-weight: 600;
                }

                .hero-copy {
                    max-width: 980px;
                    margin: 1.65rem 0 0 0;
                    font-size: clamp(1.35rem, 1.65vw, 1.55rem);
                    line-height: 1.62;
                    color: var(--muted);
                }

                .hero-actions {
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: 1.6rem;
                    margin-top: 2.35rem;
                    width: 100%;
                    max-width: 100%;
                }

                .hero-action-card {
                    background: var(--paper);
                    border: 1px solid var(--border);
                    border-top: 4px solid var(--accent);
                    border-radius: var(--radius-md);
                    padding: 2rem;
                    box-shadow: var(--shadow-sm);
                    min-height: 210px;
                }

                .hero-action-title {
                    font-weight: 800;
                    color: var(--foreground);
                    font-size: 1.45rem;
                    line-height: 1.2;
                    margin-bottom: 0.8rem;
                }

                .hero-action-copy {
                    color: var(--muted);
                    font-size: 1.16rem;
                    line-height: 1.55;
                }

                .hero-panel {
                    align-self: stretch;
                    background: var(--paper);
                    border: 1px solid var(--border-strong);
                    border-top: 5px solid var(--accent);
                    border-radius: var(--radius-lg);
                    padding: 2.15rem;
                    box-shadow: var(--shadow-lg);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }

                .hero-panel-title {
                    font-family: "Playfair Display", Georgia, serif;
                    font-size: 2.55rem;
                    line-height: 1.08;
                    margin: 0 0 1.45rem 0;
                    color: var(--foreground);
                }

                .meta-list {
                    display: grid;
                    gap: 1rem;
                }

                .meta-item {
                    display: flex;
                    justify-content: space-between;
                    gap: 1.25rem;
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 1rem;
                    font-size: 1.15rem;
                    line-height: 1.35;
                }

                .meta-item span:first-child {
                    color: var(--muted);
                    font-weight: 650;
                }

                .meta-item span:last-child {
                    font-weight: 850;
                    color: var(--foreground);
                    text-align: right;
                }

                /* Output preview modules: 2x2 by default so text can be large. */
                .preview-grid {
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 1.75rem;
                    margin: 0 0 3.1rem 0;
                }

                .preview-card {
                    background: var(--paper);
                    border: 1px solid var(--border);
                    border-top: 4px solid var(--accent);
                    border-radius: var(--radius-lg);
                    padding: 2.15rem;
                    min-height: 255px;
                    box-shadow: var(--shadow-md);
                }

                .preview-number {
                    font-family: "IBM Plex Mono", monospace;
                    color: var(--accent);
                    font-size: 1rem;
                    letter-spacing: 0.075em;
                    text-transform: uppercase;
                    margin-bottom: 1rem;
                    font-weight: 700;
                }

                .preview-title {
                    font-family: "Playfair Display", Georgia, serif;
                    font-size: 2rem;
                    line-height: 1.16;
                    color: var(--foreground);
                    margin-bottom: 0.9rem;
                }

                .preview-copy {
                    font-size: 1.22rem;
                    line-height: 1.58;
                    color: var(--muted);
                }

                .section-card {
                    background: var(--paper);
                    border: 1px solid var(--border);
                    border-top: 4px solid var(--accent);
                    border-radius: var(--radius-lg);
                    padding: 2.75rem 3rem;
                    box-shadow: var(--shadow-md);
                    margin: 2.5rem 0 2rem 0;
                }

                .section-title {
                    font-family: "Playfair Display", Georgia, serif;
                    font-size: clamp(2rem, 2.45vw, 2.65rem);
                    line-height: 1.12;
                    margin: 0.6rem 0 1rem 0;
                    color: var(--foreground);
                    max-width: 1120px;
                }

                .section-copy {
                    max-width: 1080px;
                    margin: 0;
                    color: var(--muted);
                    font-size: 1.24rem;
                    line-height: 1.65;
                }

                .metric-card {
                    background: var(--paper);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 2.25rem;
                    box-shadow: var(--shadow-md);
                    min-height: 255px;
                }

                .metric-card.gold {
                    border-top: 4px solid var(--accent);
                }

                .metric-label {
                    font-family: "IBM Plex Mono", monospace;
                    margin: 0 0 1.1rem 0;
                    color: var(--accent);
                    font-size: 1rem;
                    text-transform: uppercase;
                    letter-spacing: 0.075em;
                    font-weight: 700;
                    line-height: 1.35;
                }

                .metric-value {
                    font-family: "Playfair Display", Georgia, serif;
                    margin: 0;
                    color: var(--foreground);
                    font-size: 3.25rem;
                    font-weight: 700;
                    line-height: 1;
                    letter-spacing: -0.035em;
                }

                .metric-caption {
                    margin: 1.1rem 0 0 0;
                    color: var(--muted);
                    font-size: 1.18rem;
                    line-height: 1.55;
                }

                .empty-state {
                    display: grid;
                    grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.8fr);
                    gap: 1.75rem;
                    align-items: stretch;
                    margin: 2rem 0 2.5rem 0;
                }

                .empty-panel {
                    background: var(--paper);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 2.25rem;
                    box-shadow: var(--shadow-md);
                    min-height: 230px;
                }

                .empty-panel h3 {
                    font-size: 2.05rem;
                    margin: 0.45rem 0 0.95rem 0;
                    line-height: 1.16;
                }

                .empty-panel p {
                    margin: 0;
                    font-size: 1.2rem;
                    line-height: 1.62;
                    color: var(--muted);
                }

                .event-card {
                    background: var(--paper);
                    border: 1px solid var(--border);
                    border-top: 4px solid var(--accent);
                    border-radius: var(--radius-lg);
                    padding: 2.15rem;
                    height: 100%;
                    box-shadow: var(--shadow-md);
                }

                .event-title {
                    font-family: "Playfair Display", Georgia, serif;
                    color: var(--foreground);
                    font-size: 2rem;
                    line-height: 1.18;
                    margin-bottom: 0.65rem;
                }

                .event-subtitle {
                    color: var(--muted);
                    font-size: 1.16rem;
                    margin-bottom: 1.1rem;
                }

                .event-score {
                    display: inline-flex;
                    border-radius: 999px;
                    padding: 0.55rem 0.9rem;
                    background: rgba(169, 119, 5, 0.10);
                    border: 1px solid rgba(169, 119, 5, 0.24);
                    color: var(--accent);
                    font-family: "IBM Plex Mono", monospace;
                    font-size: 1rem;
                    font-weight: 700;
                    letter-spacing: 0.045em;
                    text-transform: uppercase;
                }

                .callout {
                    border-left: 5px solid var(--accent);
                    background: rgba(255, 255, 255, 0.84);
                    padding: 1.35rem 1.45rem;
                    color: var(--muted);
                    margin: 1.25rem 0;
                    font-size: 1.16rem;
                    line-height: 1.58;
                    border-radius: 0 16px 16px 0;
                    box-shadow: var(--shadow-sm);
                }

                div[data-testid="stTabs"] [data-baseweb="tab-list"] {
                    gap: 1rem;
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 1rem;
                    margin: 1.75rem 0 2.25rem 0;
                    align-items: center;
                    flex-wrap: wrap;
                }

                div[data-testid="stTabs"] button,
                button[data-baseweb="tab"] {
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    color: var(--muted) !important;
                    font-size: 1.22rem !important;
                    font-weight: 850 !important;
                    letter-spacing: 0.005em !important;
                    text-transform: none !important;
                    padding: 1.25rem 1.6rem !important;
                    border-radius: 999px !important;
                    border: 1px solid transparent !important;
                    min-height: 64px !important;
                }

                div[data-testid="stTabs"] button[aria-selected="true"],
                button[data-baseweb="tab"][aria-selected="true"] {
                    color: var(--foreground) !important;
                    background: rgba(169, 119, 5, 0.15) !important;
                    border: 2px solid rgba(169, 119, 5, 0.36) !important;
                    box-shadow: var(--shadow-sm);
                }

                .stButton > button,
                .stDownloadButton > button {
                    min-height: 64px;
                    border-radius: 14px;
                    border: 1px solid var(--accent);
                    background: var(--accent);
                    color: white;
                    font-family: "Source Sans 3", system-ui, sans-serif;
                    font-size: 1.2rem;
                    font-weight: 900;
                    letter-spacing: 0.01em;
                    box-shadow: var(--shadow-md);
                    transition: all 180ms ease-out;
                }

                .stButton > button:hover,
                .stDownloadButton > button:hover {
                    background: var(--accent-soft);
                    border-color: var(--accent-soft);
                    color: white;
                    box-shadow: var(--shadow-lg);
                    transform: translateY(-1px);
                }

                [data-testid="stDataFrame"] {
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    overflow: hidden;
                    box-shadow: var(--shadow-sm);
                    font-size: 1.05rem;
                }

                [data-testid="stStatusWidget"] {
                    border-radius: var(--radius-lg);
                    border: 1px solid var(--border);
                    background: var(--paper);
                    box-shadow: var(--shadow-md);
                    font-size: 1.1rem;
                }

                .stAlert {
                    font-size: 1.12rem;
                }

                input, textarea, select {
                    border-radius: 12px !important;
                    font-size: 1.1rem !important;
                }

                @media (max-width: 1500px) {
                    .hero {
                        grid-template-columns: minmax(0, 1fr);
                    }

                    .hero-panel {
                        max-width: none;
                    }
                }

                @media (max-width: 1200px) {
                    .block-container {
                        padding: 1.2rem 1.2rem 5rem 1.2rem !important;
                    }

                    .preview-grid,
                    .empty-state {
                        grid-template-columns: 1fr;
                    }

                    .hero-actions {
                        grid-template-columns: 1fr;
                    }

                    .hero {
                        padding: 2.25rem;
                    }
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _sidebar_controls(self) -> dict[str, object]:
        """Render sidebar controls and return selected values."""

        st.sidebar.markdown("### Study Setup")
        st.sidebar.caption("Choose a company universe, filing depth, and comparison method.")

        mode = st.sidebar.radio(
            "Analysis mode",
            options=["Single ticker", "Batch universe"],
            index=0,
        )

        if mode == "Single ticker":
            ticker_input = st.sidebar.text_input(
                "Ticker",
                value="AAPL",
                help="Enter one public company ticker, such as AAPL, MSFT, TSLA, or NVDA.",
            )
            tickers = [ticker_input.upper().strip()] if ticker_input.strip() else []
        else:
            universe_input = st.sidebar.text_area(
                "Tickers",
                value=DEFAULT_UNIVERSE,
                help="Enter tickers separated by spaces, commas, or new lines.",
                height=150,
            )
            tickers = self._parse_tickers(universe_input)

        limit = st.sidebar.slider(
            "Filings per ticker",
            min_value=3,
            max_value=20,
            value=8,
            step=1,
            help="More filings gives better summaries but takes longer to run.",
        )

        compare_mode = st.sidebar.selectbox(
            "Comparison mode",
            options=["same-form", "previous"],
            index=0,
            help="same-form compares 10-Q to previous 10-Q and 10-K to previous 10-K.",
        )

        benchmark = st.sidebar.text_input(
            "Benchmark",
            value="^GSPC",
            help="Benchmark ticker used for abnormal returns.",
        ).strip()

        top_n = st.sidebar.slider(
            "Top events",
            min_value=1,
            max_value=25,
            value=10,
            step=1,
        )

        st.sidebar.markdown(
            """
            <div class="callout">
                <strong>Recommended:</strong> keep <code>same-form</code> on. It compares
                quarterly filings with quarterly filings and annual filings with annual filings.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return {
            "mode": mode,
            "tickers": tickers,
            "limit": limit,
            "compare_mode": compare_mode,
            "benchmark": benchmark,
            "top_n": top_n,
        }

    def _render_hero(self, controls: dict[str, object]) -> None:
        """Render the hero section."""

        tickers = list(controls["tickers"])
        mode = str(controls["mode"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])
        limit = int(controls["limit"])
        universe_label = f"{len(tickers)} tickers" if len(tickers) > 1 else (tickers[0] if tickers else "None")

        st.markdown(
            f"""
            <section class="hero">
                <div class="hero-main">
                    <div class="label-row">
                        <span class="label-line"></span>
                        <span class="small-caps">SEC Filing Risk Analysis</span>
                    </div>
                    <h1 class="hero-title">Analyze SEC risk disclosures and <em>test market reactions.</em></h1>
                    <p class="hero-copy">
                        A research terminal for measuring how corporate risk language changes, then checking
                        whether those changes line up with post-filing returns, volatility, and abnormal returns.
                    </p>
                    <div class="hero-actions">
                        <div class="hero-action-card">
                            <div class="hero-action-title">1. Choose a universe</div>
                            <div class="hero-action-copy">Start with one ticker or run a small cross-company study.</div>
                        </div>
                        <div class="hero-action-card">
                            <div class="hero-action-title">2. Run a study</div>
                            <div class="hero-action-copy">Score disclosure changes and connect them to market outcomes.</div>
                        </div>
                        <div class="hero-action-card">
                            <div class="hero-action-title">3. Read the evidence</div>
                            <div class="hero-action-copy">Inspect score buckets, top events, and abnormal returns.</div>
                        </div>
                    </div>
                </div>
                <aside class="hero-panel">
                    <h2 class="hero-panel-title">Current study</h2>
                    <div class="meta-list">
                        <div class="meta-item"><span>Mode</span><span>{escape(mode)}</span></div>
                        <div class="meta-item"><span>Universe</span><span>{escape(universe_label)}</span></div>
                        <div class="meta-item"><span>Filings</span><span>{limit} per ticker</span></div>
                        <div class="meta-item"><span>Comparison</span><span>{escape(compare_mode)}</span></div>
                        <div class="meta-item"><span>Benchmark</span><span>{escape(benchmark)}</span></div>
                    </div>
                </aside>
            </section>
            """,
            unsafe_allow_html=True,
        )

    def _render_result_preview(self) -> None:
        """Render immediate value preview before the user clicks anything."""

        st.markdown(
            """
            <div class="preview-grid">
                <div class="preview-card">
                    <div class="preview-number">Output 01</div>
                    <div class="preview-title">Risk-change score</div>
                    <div class="preview-copy">A bounded score showing how much risk-factor language changed versus a prior filing.</div>
                </div>
                <div class="preview-card">
                    <div class="preview-number">Output 02</div>
                    <div class="preview-title">Top changed terms</div>
                    <div class="preview-copy">A readable list of added and removed risk themes for qualitative inspection.</div>
                </div>
                <div class="preview-card">
                    <div class="preview-number">Output 03</div>
                    <div class="preview-title">Market reaction</div>
                    <div class="preview-copy">Post-filing returns, realized volatility, benchmark returns, and abnormal returns.</div>
                </div>
                <div class="preview-card">
                    <div class="preview-number">Output 04</div>
                    <div class="preview-title">Research evidence</div>
                    <div class="preview-copy">Low, medium, and high disclosure-change buckets for quick interpretation.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _section_header(self, label: str, title: str, copy: str) -> None:
        """Render a reusable editorial section header."""

        st.markdown(
            f"""
            <div class="section-card">
                <div class="small-caps">{escape(label)}</div>
                <h2 class="section-title">{escape(title)}</h2>
                <p class="section-copy">{escape(copy)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_overview_tab(self, controls: dict[str, object]) -> None:
        """Render overview and quick analysis metrics."""

        self._section_header(
            "Overview",
            "Run the full research loop in one pass.",
            "This executes disclosure extraction, NLP risk scoring, event-study analysis, and a bucketed research summary.",
        )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            self._metric_card("Signal", "Risk text", "SEC 10-K and 10-Q Item 1A disclosures.")
        with col_b:
            self._metric_card("Scoring", "NLP", "TF-IDF change, uncertainty terms, and negative terms.")
        with col_c:
            self._metric_card("Test", "Event study", "Returns, volatility, and abnormal returns.")

        self._empty_state(
            "What happens when you run this?",
            "The app will fetch filings, score risk-language changes, calculate market reaction metrics, and summarize the evidence in a table you can download.",
            "Best first run: AAPL, 8 filings, same-form comparison.",
        )

        if st.button("Run full risk analysis", use_container_width=True):
            with st.status("Running full research workflow...", expanded=True) as status:
                st.write("Fetching SEC filings and extracting risk sections...")
                st.write("Scoring disclosure-language changes...")
                st.write("Calculating returns, volatility, and abnormal returns...")
                event_df = self._get_event_study_any(controls)
                summary_df = self._get_summary_any(controls)
                status.update(label="Research workflow complete.", state="complete")

            self._render_overview_metrics(event_df, summary_df)
            self._display_dataframe_with_download(summary_df, file_name=self._file_name(controls, "research_summary.csv"))

    def _render_risk_signal_tab(self, controls: dict[str, object]) -> None:
        """Render NLP risk-change signal analysis."""

        self._section_header(
            "Risk Signal",
            "Measure disclosure change without pretending it is magic.",
            "The score shows how much risk language changed. It is useful for research and inspection, not as a standalone trading signal.",
        )

        tickers = list(controls["tickers"])
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])

        if not tickers:
            st.warning("Enter at least one ticker.")
            return

        ticker = tickers[0]
        if len(tickers) > 1:
            st.info("Risk signal charts are shown for the first ticker. Use Research Summary or Top Events for batch mode.")

        self._empty_state(
            "Expected output",
            "You will get one row per filing comparison with final risk score, TF-IDF change, word-count change, negative-term change, uncertainty-term change, and top changed terms.",
            "Use this tab when you want to inspect the text signal itself.",
        )

        if st.button("Calculate risk signal", use_container_width=True):
            with st.status(f"Scoring risk disclosures for {ticker}...", expanded=True) as status:
                st.write("Downloading recent filings...")
                st.write("Extracting Item 1A risk sections...")
                st.write("Comparing current and prior risk language...")
                df = self._get_scores(ticker, limit, compare_mode)
                status.update(label="Risk signal complete.", state="complete")

            self._render_signal_metrics(df)
            self._display_dataframe_with_download(df, file_name=f"{ticker.lower()}_risk_scores.csv")

            chart_df = self._prepare_date_chart_df(df, "current_filing_date", "final_risk_change_score")
            if not chart_df.empty:
                st.markdown("### Risk-change score over time")
                st.line_chart(chart_df, x="current_filing_date", y="final_risk_change_score", use_container_width=True)

    def _render_market_reaction_tab(self, controls: dict[str, object]) -> None:
        """Render event-study market reaction analysis."""

        self._section_header(
            "Market Reaction",
            "Connect language changes to market outcomes.",
            "Run an event study around the filing date using post-filing returns, realized volatility, benchmark returns, and abnormal returns.",
        )

        if not controls["tickers"]:
            st.warning("Enter at least one ticker.")
            return

        self._empty_state(
            "Expected output",
            "You will see post-filing returns over multiple windows, annualized realized volatility, benchmark returns, and abnormal returns.",
            "Use this tab when you want to test whether text changes line up with price behavior.",
        )

        button_label = "Run batch event study" if len(controls["tickers"]) > 1 else "Run event study"
        if st.button(button_label, use_container_width=True):
            with st.status("Running event study...", expanded=True) as status:
                st.write("Building risk-change scores...")
                st.write("Downloading market and benchmark prices...")
                st.write("Calculating post-filing returns, volatility, and abnormal returns...")
                df = self._get_event_study_any(controls)
                status.update(label="Event study complete.", state="complete")

            self._render_market_metrics(df)
            self._display_dataframe_with_download(df, file_name=self._file_name(controls, "event_study.csv"))
            chart_df = self._clean_chart_df(df, ["final_risk_change_score", "abnormal_return_20d", "post_vol_20d"])

            if not chart_df.empty:
                left, right = st.columns(2)
                with left:
                    st.markdown("### Risk score vs. 20D abnormal return")
                    st.scatter_chart(chart_df, x="final_risk_change_score", y="abnormal_return_20d", use_container_width=True)
                with right:
                    st.markdown("### Risk score vs. 20D volatility")
                    st.scatter_chart(chart_df, x="final_risk_change_score", y="post_vol_20d", use_container_width=True)

    def _render_summary_tab(self, controls: dict[str, object]) -> None:
        """Render research summary by risk-score bucket."""

        self._section_header(
            "Research Summary",
            "See whether high-disclosure-change filings behave differently after release.",
            "The app groups filings into low, medium, and high change buckets, then compares average market outcomes across those buckets.",
        )

        if not controls["tickers"]:
            st.warning("Enter at least one ticker.")
            return

        self._empty_state(
            "Expected output",
            "You will get a compact table showing filing count, average risk score, average returns, abnormal returns, and realized volatility by risk bucket.",
            "This is the easiest table to explain in a portfolio walkthrough.",
        )

        if st.button("Build research summary", use_container_width=True):
            with st.status("Building risk-bucket summary...", expanded=True) as status:
                st.write("Running event study inputs...")
                st.write("Sorting filings into low, medium, and high disclosure-change buckets...")
                st.write("Aggregating return and volatility outcomes...")
                df = self._get_summary_any(controls)
                status.update(label="Research summary complete.", state="complete")

            self._display_dataframe_with_download(df, file_name=self._file_name(controls, "summary.csv"))

            if not df.empty:
                col_a, col_b = st.columns(2)
                with col_a:
                    if "avg_post_vol_20d" in df.columns:
                        st.markdown("### Average 20D realized volatility")
                        st.bar_chart(df, x="risk_score_bucket", y="avg_post_vol_20d")
                with col_b:
                    if "avg_abnormal_return_20d" in df.columns:
                        st.markdown("### Average 20D abnormal return")
                        st.bar_chart(df, x="risk_score_bucket", y="avg_abnormal_return_20d")

    def _render_top_events_tab(self, controls: dict[str, object]) -> None:
        """Render highest risk-change filing events."""

        self._section_header(
            "Top Events",
            "Find the filings with the largest risk-language changes.",
            "These events are useful for qualitative inspection, model debugging, and explaining the signal in interviews.",
        )

        if not controls["tickers"]:
            st.warning("Enter at least one ticker.")
            return

        self._empty_state(
            "Expected output",
            "You will see the highest-scoring filing events with dates, form types, scores, post-filing metrics, and top added terms.",
            "Use this tab when you want concrete examples instead of aggregate statistics.",
        )

        if st.button("Find top risk-change events", use_container_width=True):
            with st.status("Ranking top disclosure-change events...", expanded=True) as status:
                st.write("Building event-study table...")
                st.write("Sorting filings by final risk-change score...")
                st.write("Preparing event cards and downloadable table...")
                df = self._get_top_events_any(controls)
                status.update(label="Top events ready.", state="complete")

            self._render_event_cards(df)
            self._display_dataframe_with_download(df, file_name=self._file_name(controls, "top_events.csv"))

    def _render_methodology_tab(self) -> None:
        """Render methodology explanation."""

        self._section_header(
            "Methodology",
            "A transparent research pipeline, not a black-box prediction demo.",
            "The project favors interpretable signals, careful comparison modes, and honest limitations.",
        )

        left, right = st.columns([1.05, 0.95])
        with left:
            st.markdown(
                """
                ### Pipeline

                1. Pull recent 10-K and 10-Q filings from SEC EDGAR.
                2. Extract the Item 1A / Risk Factors section.
                3. Compare the current risk section against a previous filing.
                4. Generate NLP features:
                   - TF-IDF similarity
                   - Word-count percentage change
                   - Negative-term change
                   - Uncertainty-term change
                   - Added and removed risk terms
                5. Combine features into a bounded risk-change score.
                6. Run an event study around the filing date.
                7. Summarize results by risk-score bucket.
                """
            )

        with right:
            st.markdown(
                """
                ### Interpretation

                A high score means the filing language changed meaningfully.
                It does **not** automatically mean the stock should fall or volatility should rise.

                The strongest use of this project is exploratory research: identifying disclosure changes,
                ranking events, and testing whether the text signal has market relevance over a broader sample.
                """
            )

    def _empty_state(self, title: str, body: str, note: str) -> None:
        """Render a useful empty state before the user runs an analysis."""

        st.markdown(
            f"""
            <div class="empty-state">
                <div class="empty-panel">
                    <div class="small-caps">Before you run it</div>
                    <h3>{escape(title)}</h3>
                    <p>{escape(body)}</p>
                </div>
                <div class="empty-panel">
                    <div class="small-caps">Manager note</div>
                    <p>{escape(note)}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _get_event_study_any(self, controls: dict[str, object]) -> pd.DataFrame:
        """Return single-ticker or batch event-study results."""

        tickers = list(controls["tickers"])
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])

        if len(tickers) > 1:
            return self.pipeline.build_batch_event_study_df(
                tickers=tickers,
                limit=limit,
                compare_mode=compare_mode,
                benchmark_ticker=benchmark,
            )

        return self._get_event_study(tickers[0], limit, compare_mode, benchmark)

    def _get_summary_any(self, controls: dict[str, object]) -> pd.DataFrame:
        """Return single-ticker or batch research summary."""

        tickers = list(controls["tickers"])
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])

        if len(tickers) > 1:
            return self.pipeline.build_batch_research_summary_df(
                tickers=tickers,
                limit=limit,
                compare_mode=compare_mode,
                benchmark_ticker=benchmark,
            )

        return self._get_summary(tickers[0], limit, compare_mode, benchmark)

    def _get_top_events_any(self, controls: dict[str, object]) -> pd.DataFrame:
        """Return single-ticker or batch top risk events."""

        tickers = list(controls["tickers"])
        limit = int(controls["limit"])
        compare_mode = str(controls["compare_mode"])
        benchmark = str(controls["benchmark"])
        top_n = int(controls["top_n"])

        if len(tickers) > 1:
            return self.pipeline.build_batch_top_risk_events_df(
                tickers=tickers,
                limit=limit,
                compare_mode=compare_mode,
                benchmark_ticker=benchmark,
                n=top_n,
            )

        return self.pipeline.build_top_risk_events_df(
            ticker=tickers[0],
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark,
            n=top_n,
        )

    def _render_overview_metrics(self, event_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
        """Render high-level analysis metrics."""

        valid_df = self._valid_event_rows(event_df)
        if valid_df.empty:
            st.warning("No valid event-study rows were returned.")
            return

        avg_score = valid_df["final_risk_change_score"].mean()
        avg_abnormal = valid_df["abnormal_return_20d"].mean() if "abnormal_return_20d" in valid_df.columns else pd.NA

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            self._metric_card("Companies", str(valid_df["ticker"].nunique()), "Unique tickers analyzed.")
        with col_b:
            self._metric_card("Events", str(len(valid_df)), "Filing comparisons.")
        with col_c:
            self._metric_card("Avg Risk Score", self._format_number(avg_score), "Average disclosure-change score.")
        with col_d:
            self._metric_card("Avg 20D Abnormal", self._format_pct(avg_abnormal), "Benchmark-adjusted return.")

        if not summary_df.empty:
            st.markdown("### Bucket summary")
            self._display_dataframe_with_download(summary_df, "overview_summary.csv")

    def _render_signal_metrics(self, df: pd.DataFrame) -> None:
        """Render metric cards for risk scores."""

        if df.empty or "final_risk_change_score" not in df.columns:
            return

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            self._metric_card("Comparisons", str(len(df)), "Filing pairs scored.")
        with col_b:
            self._metric_card("Avg Score", self._format_number(df["final_risk_change_score"].mean()), "Mean score.")
        with col_c:
            self._metric_card("Max Score", self._format_number(df["final_risk_change_score"].max()), "Largest change.")

    def _render_market_metrics(self, df: pd.DataFrame) -> None:
        """Render metric cards for event-study outputs."""

        valid_df = self._valid_event_rows(df)
        if valid_df.empty:
            return

        avg_abnormal_20d = valid_df["abnormal_return_20d"].mean() if "abnormal_return_20d" in valid_df.columns else pd.NA
        avg_vol_20d = valid_df["post_vol_20d"].mean() if "post_vol_20d" in valid_df.columns else pd.NA

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            self._metric_card("Events", str(len(valid_df)), "Valid filing events.")
        with col_b:
            self._metric_card("Avg 20D Abnormal", self._format_pct(avg_abnormal_20d), "Benchmark-adjusted return.")
        with col_c:
            self._metric_card("Avg 20D Vol", self._format_pct(avg_vol_20d), "Annualized volatility.")

    def _render_event_cards(self, df: pd.DataFrame) -> None:
        """Render top event cards."""

        if df.empty:
            return

        top_df = df.head(3)
        columns = st.columns(len(top_df))

        for column, (_, row) in zip(columns, top_df.iterrows()):
            ticker = escape(str(row.get("ticker", "")))
            date = escape(str(row.get("current_filing_date", "")))
            form_type = escape(str(row.get("current_form_type", "")))
            score = self._format_number(row.get("final_risk_change_score"))
            terms = escape(str(row.get("top_added_terms", "No terms available")))

            with column:
                st.markdown(
                    f"""
                    <div class="event-card">
                        <div class="event-title">{ticker} · {form_type}</div>
                        <div class="event-subtitle">{date}</div>
                        <div class="event-score">Risk score: {score}</div>
                        <p style="margin-top: 0.85rem; color: #6B6B6B;">
                            Added terms: {terms}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    @staticmethod
    def _metric_card(label: str, value: str, caption: str) -> None:
        """Render a custom metric card."""

        st.markdown(
            f"""
            <div class="metric-card gold">
                <p class="metric-label">{escape(label)}</p>
                <h3 class="metric-value">{escape(value)}</h3>
                <p class="metric-caption">{escape(caption)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def _parse_tickers(raw_text: str) -> list[str]:
        """Parse ticker text separated by spaces, commas, or new lines."""

        normalized = raw_text.replace(",", " ").replace("\n", " ")
        tickers = [token.upper().strip() for token in normalized.split(" ") if token.strip()]
        return list(dict.fromkeys(tickers))

    def _display_dataframe_with_download(self, df: pd.DataFrame, file_name: str) -> None:
        """Display a DataFrame and provide a CSV download button."""

        if df.empty:
            st.warning("No rows returned.")
            return

        display_df = self._round_numeric(df)
        st.dataframe(display_df, use_container_width=True, height=min(650, 180 + 38 * max(len(display_df), 1)))

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=file_name,
            mime="text/csv",
            use_container_width=True,
            key=f"download_{file_name}_{len(df)}_{len(df.columns)}",
        )

    @staticmethod
    def _valid_event_rows(df: pd.DataFrame) -> pd.DataFrame:
        """Return event-study rows with valid risk scores."""

        if df.empty or "final_risk_change_score" not in df.columns:
            return pd.DataFrame()
        return df.dropna(subset=["final_risk_change_score"]).copy()

    @staticmethod
    def _clean_chart_df(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Return chart-ready numeric data."""

        if df.empty:
            return pd.DataFrame()

        available_columns = [column for column in columns if column in df.columns]
        if not available_columns:
            return pd.DataFrame()

        chart_df = df[available_columns].copy()
        for column in available_columns:
            chart_df[column] = pd.to_numeric(chart_df[column], errors="coerce")
        return chart_df.dropna()

    @staticmethod
    def _round_numeric(df: pd.DataFrame) -> pd.DataFrame:
        """Round numeric columns for cleaner display."""

        display_df = df.copy()
        numeric_columns = display_df.select_dtypes(include="number").columns
        display_df[numeric_columns] = display_df[numeric_columns].round(4)
        return display_df

    @staticmethod
    def _prepare_date_chart_df(df: pd.DataFrame, date_column: str, value_column: str) -> pd.DataFrame:
        """Prepare a clean date/value DataFrame for Streamlit charts."""

        if df.empty or date_column not in df.columns or value_column not in df.columns:
            return pd.DataFrame()

        chart_df = df[[date_column, value_column]].copy()
        chart_df[date_column] = pd.to_datetime(chart_df[date_column], errors="coerce")
        chart_df[value_column] = pd.to_numeric(chart_df[value_column], errors="coerce")
        chart_df = chart_df.dropna(subset=[date_column, value_column])
        chart_df = chart_df.sort_values(date_column)
        return chart_df

    @staticmethod
    def _file_name(controls: dict[str, object], suffix: str) -> str:
        """Create a clean output file name."""

        tickers = list(controls["tickers"])
        prefix = tickers[0].lower() if len(tickers) == 1 else "batch"
        return f"{prefix}_{suffix}"

    @staticmethod
    def _format_number(value: object) -> str:
        """Format a number for metric display."""

        if pd.isna(value):
            return "n/a"
        try:
            return f"{float(value):.3f}"
        except (TypeError, ValueError):
            return "n/a"

    @staticmethod
    def _format_pct(value: object) -> str:
        """Format decimal return/volatility as a percentage."""

        if pd.isna(value):
            return "n/a"
        try:
            return f"{float(value) * 100:.2f}%"
        except (TypeError, ValueError):
            return "n/a"

    @st.cache_data(show_spinner=False)
    def _get_scores(_self, ticker: str, limit: int, compare_mode: str) -> pd.DataFrame:
        """Cached risk-score query."""

        return _self.pipeline.build_risk_change_scores_df(ticker=ticker, limit=limit, compare_mode=compare_mode)

    @st.cache_data(show_spinner=False)
    def _get_event_study(_self, ticker: str, limit: int, compare_mode: str, benchmark: str) -> pd.DataFrame:
        """Cached event-study query."""

        return _self.pipeline.build_event_study_df(
            ticker=ticker,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark,
        )

    @st.cache_data(show_spinner=False)
    def _get_summary(_self, ticker: str, limit: int, compare_mode: str, benchmark: str) -> pd.DataFrame:
        """Cached research-summary query."""

        return _self.pipeline.build_research_summary_df(
            ticker=ticker,
            limit=limit,
            compare_mode=compare_mode,
            benchmark_ticker=benchmark,
        )


if __name__ == "__main__":
    RiskDashboardApp().run()
