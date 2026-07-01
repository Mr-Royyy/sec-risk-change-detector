"""Streamlit dashboard for the SEC Risk Change Detector.

This file only refactors the frontend experience. The backend pipeline and
analysis methods are unchanged.
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

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
        """Inject the institutional research-terminal design system."""

        st.markdown(
            """
                        <style>
                @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700;800;900&display=swap');

                .stApp {
                    --bg:#F3F6FA; --surface:#FFFFFF; --subtle:#F8FAFC; --sidebar:#0B1220; --sidebar-soft:#111B2C;
                    --text:#111827; --heading:#0B1220; --secondary:#475569; --tertiary:#64748B;
                    --border:#CBD5E1; --border-soft:#E2E8F0; --border-strong:#94A3B8;
                    --primary:#0F2742; --primary-hover:#162C46; --primary-border:#294C73; --active:#2563EB;
                    --radius-sm:4px; --radius-md:6px; --radius-lg:8px; --sidebar-width:280px; --content-max:1600px;
                    background:var(--bg); color:var(--text); font-family:"Source Sans 3", system-ui, sans-serif;
                }

                .block-container{max-width:none!important;width:100%!important;padding:1.05rem 1.35rem 4rem!important;}
                .page-shell{width:min(100%,var(--content-max));max-width:var(--content-max);margin:0 auto;font-family:"Source Sans 3",system-ui,sans-serif;}
                .page-shell p,.page-shell li{color:var(--secondary);font-size:clamp(15px,.9vw,17px);line-height:1.5;}
                .page-shell h3{color:var(--heading);font-size:clamp(22px,1.45vw,28px);line-height:1.18;font-weight:850;margin:.8rem 0 .5rem;}

                header button,[data-testid="stToolbar"] button,[data-testid="stDecoration"] button{width:auto!important;min-width:0!important;min-height:initial!important;padding:initial!important;border-radius:initial!important;background:transparent!important;border:none!important;box-shadow:none!important;color:inherit!important;-webkit-text-fill-color:inherit!important;font-size:inherit!important;font-weight:inherit!important;}

                section[data-testid="stSidebar"]{width:var(--sidebar-width)!important;min-width:var(--sidebar-width)!important;background:var(--sidebar)!important;border-right:1px solid #1E293B!important;box-shadow:none!important;}
                section[data-testid="stSidebar"]>div{width:var(--sidebar-width)!important;min-width:var(--sidebar-width)!important;padding-left:1.05rem!important;padding-right:1.05rem!important;}
                [data-testid="stSidebar"] section{padding-top:.95rem!important;}
                [data-testid="stSidebar"] h3{font-size:clamp(22px,1.35vw,26px)!important;font-weight:900!important;margin:0 0 .3rem!important;color:#fff!important;letter-spacing:-.02em!important;}
                [data-testid="stSidebar"] .stCaptionContainer,[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#CBD5E1!important;font-size:14px!important;line-height:1.4!important;margin-bottom:1rem!important;}
                [data-testid="stSidebar"] label{color:#F8FAFC!important;font-size:15px!important;font-weight:750!important;text-transform:none!important;margin-bottom:.25rem!important;}
                [data-testid="stSidebar"] .stTextInput,[data-testid="stSidebar"] .stTextArea,[data-testid="stSidebar"] .stSelectbox,[data-testid="stSidebar"] .stRadio,[data-testid="stSidebar"] .stSlider{margin-bottom:.95rem!important;padding-bottom:.85rem!important;border-bottom:1px solid rgba(148,163,184,.28)!important;}
                [data-testid="stSidebar"] input,[data-testid="stSidebar"] textarea,[data-testid="stSidebar"] select,[data-testid="stSidebar"] [data-baseweb="select"]>div,[data-testid="stSidebar"] [data-baseweb="input"],[data-testid="stSidebar"] [data-baseweb="base-input"],[data-testid="stSidebar"] [data-baseweb="textarea"]{min-height:42px!important;font-size:15px!important;border-radius:6px!important;background:#F8FAFC!important;border-color:#94A3B8!important;color:#0B1220!important;opacity:1!important;-webkit-text-fill-color:#0B1220!important;}
                [data-testid="stSidebar"] [data-baseweb="select"] div,[data-testid="stSidebar"] [data-baseweb="select"] span,[data-testid="stSidebar"] [data-baseweb="input"] input,[data-testid="stSidebar"] [data-baseweb="textarea"] textarea{color:#0B1220!important;opacity:1!important;-webkit-text-fill-color:#0B1220!important;font-size:15px!important;}
                [data-testid="stSidebar"] [role="radiogroup"] label,[data-testid="stSidebar"] [data-baseweb="radio"] span,[data-testid="stSidebar"] [data-baseweb="slider"] div,[data-testid="stSidebar"] [data-baseweb="slider"] span{color:#E5EDF7!important;opacity:1!important;font-size:14px!important;}
                [data-testid="stSidebar"] .callout{background:var(--sidebar-soft)!important;border:1px solid #334155!important;border-left:4px solid #5B7FA6!important;color:#E5EDF7!important;font-size:14px!important;line-height:1.45!important;padding:.9rem!important;border-radius:6px!important;margin:.9rem 0!important;box-shadow:none!important;}
                [data-testid="stSidebar"] .callout strong{color:#fff!important;font-weight:850!important;}
                [data-testid="stSidebar"] .callout code{display:inline-block;background:#E5EDF7!important;color:#0B1220!important;-webkit-text-fill-color:#0B1220!important;border:1px solid #94A3B8!important;border-radius:5px!important;padding:.1rem .32rem!important;font-size:.95em!important;font-weight:800!important;}

                .terminal-header,.report-module,.report-section-header,.metric-card,.analysis-note,.event-card{background:var(--surface);border:1px solid var(--border);border-radius:8px;box-shadow:none;}
                .terminal-header{margin:0 0 1.1rem;overflow:hidden;}
                .terminal-topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:.65rem 1rem;background:#EAF0F7;border-bottom:1px solid var(--border);}
                .terminal-label{display:inline-flex;align-items:center;gap:.5rem;font-family:"IBM Plex Mono",monospace;font-size:14px;font-weight:750;letter-spacing:.035em;text-transform:uppercase;color:var(--primary);}
                .terminal-label::before{content:"";display:inline-block;width:.55rem;height:.55rem;background:var(--primary);border-radius:2px;}
                .terminal-timestamp{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--secondary);font-weight:600;}
                .terminal-body{display:grid;grid-template-columns:minmax(0,8fr) minmax(330px,4fr);gap:1rem;padding:1rem;align-items:stretch;}
                .terminal-main{align-self:center;}
                .terminal-title{font-size:clamp(30px,2.5vw,46px)!important;line-height:1.02!important;font-weight:900!important;margin:0!important;color:var(--heading)!important;letter-spacing:-.025em!important;max-width:1050px;}
                .terminal-title em{font-style:normal;color:var(--heading);}
                .terminal-copy{max-width:1120px;margin:.65rem 0 0;font-size:clamp(15px,1vw,17px)!important;line-height:1.45!important;color:var(--secondary)!important;font-weight:500;}
                .workflow-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin-top:.9rem;border:1px solid var(--border);border-radius:6px;overflow:hidden;background:var(--subtle);}
                .workflow-step{padding:.85rem .95rem;border-right:1px solid var(--border);min-height:94px;}
                .workflow-step:last-child{border-right:0;}
                .workflow-title{color:var(--heading);font-size:clamp(17px,1.1vw,21px);font-weight:850;margin-bottom:.2rem;}
                .workflow-copy{color:var(--secondary);font-size:clamp(14px,.9vw,16px);line-height:1.35;font-weight:500;}
                .study-panel{background:var(--subtle);border:1px solid var(--border-strong);border-radius:8px;padding:.9rem;align-self:stretch;display:flex;flex-direction:column;justify-content:center;}
                .study-panel-title{font-size:clamp(20px,1.2vw,24px);font-weight:850;color:var(--heading);margin:0 0 .55rem;}
                .study-table{display:grid;border:1px solid var(--border);background:var(--surface);border-radius:6px;overflow:hidden;}
                .study-row{display:grid;grid-template-columns:.45fr .55fr;align-items:center;gap:.8rem;padding:.55rem .7rem;border-bottom:1px solid var(--border-soft);font-size:14px;min-height:38px;}
                .study-row:last-child{border-bottom:0;}
                .study-row span:first-child{color:var(--secondary);font-weight:750;}.study-row span:last-child{color:var(--heading);font-weight:850;text-align:right;word-break:break-word;}

                .module-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.9rem;margin:0 0 1.1rem;}
                .report-module{padding:1rem;min-height:138px;}
                .module-label,.section-kicker,.metric-label{font-family:"IBM Plex Mono",monospace;color:var(--tertiary);font-size:13px;letter-spacing:.035em;text-transform:uppercase;font-weight:750;}
                .module-label{margin-bottom:.45rem;}.module-title{font-size:clamp(18px,1.15vw,22px);font-weight:850;line-height:1.15;color:var(--heading);margin-bottom:.3rem;}.module-copy{font-size:clamp(14px,.9vw,16px);line-height:1.4;color:var(--secondary);font-weight:500;}
                .report-section-header{padding:1.05rem 1.15rem;margin:1rem 0 .8rem;}.section-kicker{color:var(--primary);margin-bottom:.25rem;}.section-title{font-size:clamp(24px,1.8vw,34px)!important;font-weight:900!important;line-height:1.1!important;margin:0 0 .35rem!important;color:var(--heading)!important;max-width:1180px;}.section-copy{max-width:1220px;margin:0;color:var(--secondary);font-size:clamp(15px,.95vw,17px)!important;line-height:1.45!important;font-weight:500;}
                .metric-card{padding:1rem;min-height:132px;}.metric-card.gold{border-top:0;}.metric-label{margin:0 0 .5rem;}.metric-value{margin:0;color:var(--heading);font-size:clamp(28px,2vw,40px);font-weight:900;line-height:1;letter-spacing:-.02em;}.metric-caption{margin:.55rem 0 0;color:var(--secondary);font-size:clamp(14px,.9vw,16px);line-height:1.4;font-weight:500;}
                .analysis-prep-grid{display:grid;grid-template-columns:minmax(0,7fr) minmax(320px,5fr);gap:.9rem;align-items:stretch;margin:.9rem 0 1rem;}.analysis-note{padding:1rem;min-height:120px;}.analysis-note h3{font-size:clamp(19px,1.2vw,24px)!important;font-weight:850!important;margin:.25rem 0 .35rem!important;line-height:1.12!important;color:var(--heading)!important;}.analysis-note p{margin:0;font-size:clamp(14px,.9vw,16px)!important;line-height:1.42!important;color:var(--secondary)!important;font-weight:500;}
                .event-card{padding:1rem;height:100%;}.event-title{color:var(--heading);font-size:clamp(18px,1.1vw,22px);font-weight:850;line-height:1.15;margin-bottom:.25rem;}.event-subtitle{color:var(--secondary);font-size:14px;margin-bottom:.65rem;font-weight:600;}.event-score{display:inline-flex;border-radius:4px;padding:.32rem .5rem;background:#EEF2F6;border:1px solid var(--border);color:var(--primary);font-family:"IBM Plex Mono",monospace;font-size:13px;font-weight:750;letter-spacing:.02em;text-transform:uppercase;}

                div[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:0;border:1px solid var(--border);border-bottom:1px solid var(--border);padding-bottom:0;margin:1rem 0;background:var(--surface);border-radius:8px 8px 0 0;overflow-x:auto;}
                div[data-testid="stTabs"] button,div[data-testid="stTabs"] button[data-baseweb="tab"]{font-family:"Source Sans 3",system-ui,sans-serif!important;color:var(--secondary)!important;font-size:clamp(15px,.95vw,17px)!important;font-weight:800!important;padding:.8rem 1.05rem!important;border-radius:0!important;border:0!important;border-right:1px solid var(--border)!important;border-bottom:4px solid transparent!important;background:transparent!important;min-height:50px!important;}
                div[data-testid="stTabs"] button[aria-selected="true"],div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]{color:var(--heading)!important;background:#F8FAFC!important;border-bottom:4px solid var(--active)!important;box-shadow:none;}

                .stButton>button,.stDownloadButton>button,div[data-testid="stFormSubmitButton"]>button{min-height:46px!important;padding:.65rem 1.1rem!important;border-radius:6px!important;border:1px solid var(--primary-border)!important;background:var(--primary)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;font-family:"Source Sans 3",system-ui,sans-serif!important;font-size:clamp(15px,.9vw,17px)!important;font-weight:700!important;box-shadow:0 1px 2px rgba(15,23,42,.14)!important;cursor:pointer!important;}
                .stButton>button *,.stButton>button p,.stButton>button span,.stDownloadButton>button *,.stDownloadButton>button p,.stDownloadButton>button span,div[data-testid="stFormSubmitButton"]>button *{color:#fff!important;-webkit-text-fill-color:#fff!important;font-size:clamp(15px,.9vw,17px)!important;font-weight:700!important;}
                .stButton>button:hover,.stButton>button:focus,.stButton>button:active,.stDownloadButton>button:hover,.stDownloadButton>button:focus,.stDownloadButton>button:active,div[data-testid="stFormSubmitButton"]>button:hover{background:var(--primary-hover)!important;border-color:#3B5F84!important;color:#fff!important;-webkit-text-fill-color:#fff!important;box-shadow:0 2px 6px rgba(15,23,42,.18)!important;transform:none!important;cursor:pointer!important;}
                .stButton>button[disabled],.stDownloadButton>button[disabled],div[data-testid="stFormSubmitButton"]>button[disabled]{background:#294C73!important;color:#E5EDF7!important;-webkit-text-fill-color:#E5EDF7!important;opacity:.82!important;cursor:not-allowed!important;}

                [data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:6px!important;overflow:hidden!important;box-shadow:none!important;font-size:14px!important;background:var(--surface)!important;} [data-testid="stDataFrame"] *{font-size:14px!important;} [data-testid="stDataFrame"] [role="columnheader"]{font-size:15px!important;font-weight:800!important;}
                [data-testid="stAlert"]{border-radius:6px!important;border:1px solid var(--border)!important;background:#F8FAFC!important;font-size:15px!important;}
                .table-toolbar{display:flex;justify-content:space-between;align-items:end;gap:1rem;background:var(--surface);border:1px solid var(--border);border-radius:8px 8px 0 0;padding:.95rem 1.05rem;margin-top:1rem;border-bottom:0;}.table-title{font-size:clamp(22px,1.4vw,28px)!important;font-weight:900!important;margin:0 0 .15rem!important;color:var(--heading)!important;}.table-caption{font-size:15px!important;color:var(--secondary)!important;margin:0!important;font-weight:600;}

                @media(max-width:1350px){.terminal-body{grid-template-columns:1fr}.module-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.workflow-strip{grid-template-columns:1fr}.workflow-step{border-right:0;border-bottom:1px solid var(--border)}.workflow-step:last-child{border-bottom:0}}
                @media(max-width:1100px){.block-container{padding:.9rem .9rem 3.5rem!important}.analysis-prep-grid{grid-template-columns:1fr}.module-grid{grid-template-columns:1fr}}
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
            <section class="terminal-header">
                <div class="terminal-topbar">
                    <span class="terminal-label">SEC Filing Risk Analysis</span>
                    <span class="terminal-timestamp">Internal research workbench · disclosure signal / market reaction</span>
                </div>
                <div class="terminal-body">
                    <div class="terminal-main">
                        <h1 class="terminal-title">Analyze SEC risk disclosures and test market reactions.</h1>
                        <p class="terminal-copy">
                            Internal research tool for measuring changes in corporate risk language and checking
                            whether those changes line up with post-filing returns, volatility, and abnormal returns.
                        </p>
                        <div class="workflow-strip">
                            <div class="workflow-step">
                                <div class="workflow-title">1. Configure study</div>
                                <div class="workflow-copy">Select ticker universe, filing depth, comparison mode, and benchmark.</div>
                            </div>
                            <div class="workflow-step">
                                <div class="workflow-title">2. Run analysis</div>
                                <div class="workflow-copy">Extract disclosures, score risk-language changes, and run event-study metrics.</div>
                            </div>
                            <div class="workflow-step">
                                <div class="workflow-title">3. Review report</div>
                                <div class="workflow-copy">Inspect signal strength, market reaction evidence, top events, and exportable tables.</div>
                            </div>
                        </div>
                    </div>
                    <aside class="study-panel">
                        <h2 class="study-panel-title">Current study</h2>
                        <div class="study-table">
                            <div class="study-row"><span>Mode</span><span>{escape(mode)}</span></div>
                            <div class="study-row"><span>Universe</span><span>{escape(universe_label)}</span></div>
                            <div class="study-row"><span>Filings</span><span>{limit} per ticker</span></div>
                            <div class="study-row"><span>Comparison</span><span>{escape(compare_mode)}</span></div>
                            <div class="study-row"><span>Benchmark</span><span>{escape(benchmark)}</span></div>
                        </div>
                    </aside>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )



    def _render_result_preview(self) -> None:
        """Render immediate value preview before the user clicks anything."""

        st.markdown(
            """
            <div class="module-grid">
                <div class="report-module">
                    <div class="module-label">Output 01</div>
                    <div class="module-title">Risk-change score</div>
                    <div class="module-copy">Bounded measure of how much Item 1A risk-factor language changed versus the selected prior filing.</div>
                </div>
                <div class="report-module">
                    <div class="module-label">Output 02</div>
                    <div class="module-title">Changed risk terms</div>
                    <div class="module-copy">Added and removed disclosure themes for qualitative review, model inspection, and report evidence.</div>
                </div>
                <div class="report-module">
                    <div class="module-label">Output 03</div>
                    <div class="module-title">Market reaction</div>
                    <div class="module-copy">Post-filing returns, realized volatility, benchmark returns, and abnormal returns.</div>
                </div>
                <div class="report-module">
                    <div class="module-label">Output 04</div>
                    <div class="module-title">Research evidence</div>
                    <div class="module-copy">Low, medium, and high disclosure-change buckets for report-level interpretation.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )



    def _section_header(self, label: str, title: str, copy: str) -> None:
        """Render a reusable editorial section header."""

        st.markdown(
            f"""
            <div class="report-section-header">
                <div class="section-kicker">{escape(label)}</div>
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

        _, action_col, _ = st.columns([1, 0.5, 1])
        with action_col:
            full_analysis_clicked = st.button("Run full risk analysis", use_container_width=True)

        if full_analysis_clicked:
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

        _, action_col, _ = st.columns([1, 0.5, 1])
        with action_col:
            risk_signal_clicked = st.button("Calculate risk signal", use_container_width=True)

        if risk_signal_clicked:
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
        _, action_col, _ = st.columns([1, 0.5, 1])
        with action_col:
            event_study_clicked = st.button(button_label, use_container_width=True)

        if event_study_clicked:
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

        _, action_col, _ = st.columns([1, 0.5, 1])
        with action_col:
            summary_clicked = st.button("Build research summary", use_container_width=True)

        if summary_clicked:
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

        _, action_col, _ = st.columns([1, 0.5, 1])
        with action_col:
            top_events_clicked = st.button("Find top risk-change events", use_container_width=True)

        if top_events_clicked:
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
            <div class="analysis-prep-grid">
                <div class="analysis-note">
                    <div class="section-kicker">Before running analysis</div>
                    <h3>{escape(title)}</h3>
                    <p>{escape(body)}</p>
                </div>
                <div class="analysis-note">
                    <div class="section-kicker">Analyst note</div>
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
        row_count = len(display_df)
        column_count = len(display_df.columns)

        st.markdown(
            f"""
            <div class="table-toolbar">
                <div>
                    <div class="section-kicker">Report table</div>
                    <h2 class="table-title">Analysis output</h2>
                    <p class="table-caption">
                        {row_count} rows · {column_count} columns · export file: {escape(file_name)}
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            height=min(620, 160 + 48 * max(len(display_df), 1)),
        )

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=file_name,
            mime="text/csv",
            use_container_width=False,
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
