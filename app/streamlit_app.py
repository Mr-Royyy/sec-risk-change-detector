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
        """Inject the institutional research-terminal design system."""

        st.markdown(
            """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700;800;900&display=swap');

                :root {
                    --bg: #F3F6FA;
                    --surface: #FFFFFF;
                    --surface-subtle: #F8FAFC;
                    --surface-muted: #EEF2F6;
                    --surface-sidebar: #0B1220;
                    --surface-sidebar-soft: #111B2C;

                    --text: #111827;
                    --heading: #0B1220;
                    --secondary: #475569;
                    --tertiary: #64748B;

                    --border: #CBD5E1;
                    --border-soft: #E2E8F0;
                    --border-strong: #94A3B8;

                    --primary: #1E3A5F;
                    --primary-hover: #243B53;
                    --active: #2563EB;
                    --risk: #B42318;
                    --success: #15803D;

                    --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.05);
                    --shadow-sm: 0 3px 8px rgba(15, 23, 42, 0.07);

                    --radius-sm: 4px;
                    --radius-md: 6px;
                    --radius-lg: 8px;

                    --max: 1680px;
                    --sidebar: 340px;
                    --body: 18px;
                }

                html,
                body,
                [class*="css"] {
                    font-family: "Source Sans 3", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: var(--text);
                    font-size: var(--body) !important;
                }

                .stApp {
                    background: var(--bg);
                    color: var(--text);
                }

                .stApp::before {
                    content: none;
                }

                [data-testid="stHeader"] {
                    background: rgba(243, 246, 250, 0.96);
                    backdrop-filter: blur(10px);
                    border-bottom: 1px solid var(--border);
                    height: 3.25rem;
                }

                .block-container {
                    max-width: none !important;
                    width: 100% !important;
                    padding: 0.75rem 1.25rem 5rem 1.25rem !important;
                }

                .page-shell {
                    width: min(100%, var(--max));
                    max-width: var(--max);
                    margin: 0 auto;
                }

                section[data-testid="stSidebar"] {
                    width: var(--sidebar) !important;
                    min-width: var(--sidebar) !important;
                    background: var(--surface-sidebar);
                    border-right: 1px solid #1E293B;
                    box-shadow: none;
                }

                section[data-testid="stSidebar"] > div {
                    width: var(--sidebar) !important;
                    min-width: var(--sidebar) !important;
                    padding-left: 1.35rem !important;
                    padding-right: 1.35rem !important;
                }

                [data-testid="stSidebar"] section {
                    padding-top: 1.1rem !important;
                }

                [data-testid="stSidebar"] * {
                    color: #E5E7EB !important;
                }

                [data-testid="stSidebar"] h3 {
                    font-size: 2rem !important;
                    font-weight: 900 !important;
                    margin: 0 0 0.35rem 0 !important;
                    color: #FFFFFF !important;
                    letter-spacing: -0.02em !important;
                }

                [data-testid="stSidebar"] .stCaptionContainer,
                [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                    color: #CBD5E1 !important;
                    font-size: 1.08rem !important;
                    line-height: 1.45 !important;
                    margin-bottom: 1.25rem !important;
                }

                [data-testid="stSidebar"] label {
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    color: #F8FAFC !important;
                    font-size: 1.08rem !important;
                    font-weight: 800 !important;
                    letter-spacing: 0 !important;
                    text-transform: none !important;
                    margin-bottom: 0.35rem !important;
                }

                [data-testid="stSidebar"] .stTextInput,
                [data-testid="stSidebar"] .stTextArea,
                [data-testid="stSidebar"] .stSelectbox,
                [data-testid="stSidebar"] .stRadio,
                [data-testid="stSidebar"] .stSlider {
                    margin-bottom: 1.2rem !important;
                    padding-bottom: 1rem !important;
                    border-bottom: 1px solid rgba(148, 163, 184, 0.28);
                }

                [data-testid="stSidebar"] input,
                [data-testid="stSidebar"] textarea,
                [data-testid="stSidebar"] select,
                [data-baseweb="select"] > div {
                    min-height: 52px !important;
                    font-size: 1.08rem !important;
                    border-radius: var(--radius-md) !important;
                    background: #F8FAFC !important;
                    border-color: #334155 !important;
                    color: #0F172A !important;
                }

                [data-testid="stSidebar"] input::placeholder,
                [data-testid="stSidebar"] textarea::placeholder {
                    color: #64748B !important;
                }

                [data-testid="stSidebar"] [role="radiogroup"] label {
                    font-size: 1.08rem !important;
                    font-weight: 700 !important;
                    color: #E5E7EB !important;
                }

                [data-testid="stSidebar"] [data-baseweb="slider"] div,
                [data-testid="stSidebar"] [data-baseweb="slider"] span {
                    font-size: 1rem !important;
                    color: #E5E7EB !important;
                }

                h1, h2, h3, h4 {
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    color: var(--heading) !important;
                    letter-spacing: -0.02em !important;
                }

                p, li {
                    color: var(--secondary) !important;
                    line-height: 1.55 !important;
                    font-size: 1.12rem !important;
                }

                .terminal-header {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    box-shadow: var(--shadow-xs);
                    margin: 0 0 1.25rem 0;
                    overflow: hidden;
                }

                .terminal-topbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 1rem;
                    padding: 0.8rem 1.15rem;
                    background: #EAF0F7;
                    border-bottom: 1px solid var(--border);
                }

                .terminal-label {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.55rem;
                    font-family: "IBM Plex Mono", monospace;
                    font-size: 1.02rem;
                    font-weight: 800;
                    letter-spacing: 0.035em;
                    text-transform: uppercase;
                    color: var(--primary);
                }

                .terminal-label::before {
                    content: "";
                    display: inline-block;
                    width: 0.65rem;
                    height: 0.65rem;
                    background: var(--primary);
                    border-radius: 2px;
                }

                .terminal-timestamp {
                    font-family: "IBM Plex Mono", monospace;
                    font-size: 1rem;
                    color: var(--secondary);
                    font-weight: 600;
                }

                .terminal-body {
                    display: grid;
                    grid-template-columns: minmax(0, 8fr) minmax(380px, 4fr);
                    gap: 1.25rem;
                    padding: 1.25rem;
                    align-items: stretch;
                }

                .terminal-main {
                    align-self: center;
                }

                .terminal-title {
                    font-size: clamp(3.1rem, 4vw, 4rem) !important;
                    line-height: 1 !important;
                    font-weight: 900 !important;
                    margin: 0 !important;
                    color: var(--heading) !important;
                    max-width: 1040px;
                }

                .terminal-title em {
                    font-style: normal;
                    color: var(--heading);
                }

                .terminal-copy {
                    max-width: 1120px;
                    margin: 0.85rem 0 0 0;
                    font-size: 1.35rem !important;
                    line-height: 1.42 !important;
                    color: var(--secondary) !important;
                }

                .workflow-strip {
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: 0;
                    margin-top: 1.05rem;
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    overflow: hidden;
                    background: var(--surface-subtle);
                }

                .workflow-step {
                    padding: 1rem 1.05rem;
                    border-right: 1px solid var(--border);
                    min-height: 116px;
                }

                .workflow-step:last-child {
                    border-right: 0;
                }

                .workflow-title {
                    color: var(--heading);
                    font-size: 1.35rem;
                    font-weight: 900;
                    margin-bottom: 0.25rem;
                }

                .workflow-copy {
                    color: var(--secondary);
                    font-size: 1.08rem;
                    line-height: 1.35;
                    font-weight: 500;
                }

                .study-panel {
                    background: var(--surface-subtle);
                    border: 1px solid var(--border-strong);
                    border-radius: var(--radius-lg);
                    padding: 1rem;
                    align-self: stretch;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }

                .study-panel-title {
                    font-size: 1.55rem;
                    font-weight: 900;
                    color: var(--heading);
                    margin: 0 0 0.7rem 0;
                }

                .study-table {
                    display: grid;
                    border: 1px solid var(--border);
                    background: var(--surface);
                    border-radius: var(--radius-md);
                    overflow: hidden;
                }

                .study-row {
                    display: grid;
                    grid-template-columns: 0.45fr 0.55fr;
                    align-items: center;
                    gap: 1rem;
                    padding: 0.7rem 0.85rem;
                    border-bottom: 1px solid var(--border-soft);
                    font-size: 1.02rem;
                    min-height: 46px;
                }

                .study-row:last-child {
                    border-bottom: 0;
                }

                .study-row span:first-child {
                    color: var(--secondary);
                    font-weight: 800;
                }

                .study-row span:last-child {
                    color: var(--heading);
                    font-weight: 900;
                    text-align: right;
                    word-break: break-word;
                }

                .module-grid {
                    display: grid;
                    grid-template-columns: repeat(4, minmax(0, 1fr));
                    gap: 1rem;
                    margin: 0 0 1.25rem 0;
                }

                .report-module {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 1.3rem;
                    min-height: 170px;
                    box-shadow: none;
                }

                .module-label {
                    font-family: "IBM Plex Mono", monospace;
                    color: var(--tertiary);
                    font-size: 1rem;
                    letter-spacing: 0.035em;
                    text-transform: uppercase;
                    margin-bottom: 0.55rem;
                    font-weight: 800;
                }

                .module-title {
                    font-size: 1.7rem;
                    font-weight: 900;
                    line-height: 1.1;
                    color: var(--heading);
                    margin-bottom: 0.35rem;
                }

                .module-copy {
                    font-size: 1.1rem;
                    line-height: 1.4;
                    color: var(--secondary);
                    font-weight: 500;
                }

                .report-section-header {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 1.25rem 1.4rem;
                    box-shadow: none;
                    margin: 1.1rem 0 0.85rem 0;
                }

                .section-kicker {
                    font-family: "IBM Plex Mono", monospace;
                    font-size: 1rem;
                    font-weight: 800;
                    letter-spacing: 0.035em;
                    text-transform: uppercase;
                    color: var(--primary);
                    margin-bottom: 0.25rem;
                }

                .section-title {
                    font-size: clamp(2.25rem, 2.9vw, 3rem) !important;
                    font-weight: 900 !important;
                    line-height: 1.08 !important;
                    margin: 0 0 0.45rem 0 !important;
                    color: var(--heading) !important;
                    max-width: 1180px;
                }

                .section-copy {
                    max-width: 1220px;
                    margin: 0;
                    color: var(--secondary);
                    font-size: 1.25rem !important;
                    line-height: 1.42 !important;
                    font-weight: 500;
                }

                .metric-card {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 1.3rem;
                    box-shadow: none;
                    min-height: 168px;
                }

                .metric-card.gold {
                    border-top: 0;
                }

                .metric-label {
                    font-family: "IBM Plex Mono", monospace;
                    margin: 0 0 0.65rem 0;
                    color: var(--tertiary);
                    font-size: 1rem;
                    text-transform: uppercase;
                    letter-spacing: 0.035em;
                    font-weight: 800;
                }

                .metric-value {
                    margin: 0;
                    color: var(--heading);
                    font-size: 2.65rem;
                    font-weight: 900;
                    line-height: 1;
                    letter-spacing: -0.02em;
                }

                .metric-caption {
                    margin: 0.7rem 0 0 0;
                    color: var(--secondary);
                    font-size: 1.12rem;
                    line-height: 1.4;
                    font-weight: 500;
                }

                .analysis-prep-grid {
                    display: grid;
                    grid-template-columns: minmax(0, 7fr) minmax(360px, 5fr);
                    gap: 1rem;
                    align-items: stretch;
                    margin: 1rem 0 1.2rem 0;
                }

                .analysis-note {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 1.3rem;
                    box-shadow: none;
                    min-height: 142px;
                }

                .analysis-note h3 {
                    font-size: 1.75rem !important;
                    font-weight: 900 !important;
                    margin: 0.25rem 0 0.4rem 0 !important;
                    line-height: 1.12 !important;
                    color: var(--heading) !important;
                }

                .analysis-note p {
                    margin: 0;
                    font-size: 1.15rem !important;
                    line-height: 1.42 !important;
                    color: var(--secondary) !important;
                    font-weight: 500;
                }

                .event-card {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg);
                    padding: 1.2rem;
                    height: 100%;
                    box-shadow: none;
                }

                .event-title {
                    color: var(--heading);
                    font-size: 1.55rem;
                    font-weight: 900;
                    line-height: 1.15;
                    margin-bottom: 0.25rem;
                }

                .event-subtitle {
                    color: var(--secondary);
                    font-size: 1.08rem;
                    margin-bottom: 0.75rem;
                    font-weight: 600;
                }

                .event-score {
                    display: inline-flex;
                    border-radius: var(--radius-sm);
                    padding: 0.38rem 0.6rem;
                    background: #EEF2F6;
                    border: 1px solid var(--border);
                    color: var(--primary);
                    font-family: "IBM Plex Mono", monospace;
                    font-size: 0.95rem;
                    font-weight: 800;
                    letter-spacing: 0.02em;
                    text-transform: uppercase;
                }

                .callout {
                    border: 1px solid #334155;
                    background: var(--surface-sidebar-soft);
                    padding: 1rem 1.05rem;
                    color: #E5E7EB !important;
                    margin: 1rem 0;
                    font-size: 1.05rem;
                    line-height: 1.45;
                    border-radius: var(--radius-md);
                    box-shadow: none;
                }

                .callout strong {
                    color: #FFFFFF !important;
                }

                div[data-testid="stTabs"] [data-baseweb="tab-list"] {
                    gap: 0;
                    border: 1px solid var(--border);
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 0;
                    margin: 1.25rem 0 1.2rem 0;
                    align-items: center;
                    background: var(--surface);
                    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
                    overflow-x: auto;
                }

                div[data-testid="stTabs"] button,
                button[data-baseweb="tab"] {
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    color: var(--secondary) !important;
                    font-size: 1.28rem !important;
                    font-weight: 900 !important;
                    letter-spacing: 0 !important;
                    text-transform: none !important;
                    padding: 1rem 1.45rem !important;
                    border-radius: 0 !important;
                    border: 0 !important;
                    border-right: 1px solid var(--border) !important;
                    border-bottom: 5px solid transparent !important;
                    background: transparent !important;
                    min-height: 68px !important;
                }

                div[data-testid="stTabs"] button[aria-selected="true"],
                button[data-baseweb="tab"][aria-selected="true"] {
                    color: var(--heading) !important;
                    background: #F8FAFC !important;
                    border-bottom: 5px solid var(--active) !important;
                    box-shadow: none;
                }

                .stButton > button,
                .stDownloadButton > button {
                    min-height: 60px !important;
                    border-radius: var(--radius-md) !important;
                    border: 1px solid var(--primary) !important;
                    background: var(--primary) !important;
                    color: white !important;
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    font-size: 1.18rem !important;
                    font-weight: 900 !important;
                    letter-spacing: 0 !important;
                    box-shadow: var(--shadow-xs) !important;
                    transition: background 160ms ease-out, border-color 160ms ease-out, box-shadow 160ms ease-out;
                }

                .stButton > button:hover,
                .stDownloadButton > button:hover {
                    background: var(--primary-hover) !important;
                    border-color: var(--primary-hover) !important;
                    color: white !important;
                    box-shadow: var(--shadow-sm) !important;
                    transform: none !important;
                }

                .stDownloadButton > button {
                    background: #FFFFFF !important;
                    color: var(--primary) !important;
                    border-color: var(--border-strong) !important;
                }

                .stDownloadButton > button:hover {
                    background: #F8FAFC !important;
                    color: var(--primary) !important;
                    border-color: var(--primary-hover) !important;
                }

                [data-testid="stDataFrame"] {
                    border: 1px solid var(--border) !important;
                    border-radius: var(--radius-md) !important;
                    overflow: hidden !important;
                    box-shadow: none !important;
                    font-size: 1rem !important;
                    background: var(--surface) !important;
                }

                [data-testid="stDataFrame"] * {
                    font-size: 1rem !important;
                }

                [data-testid="stDataFrame"] [role="columnheader"],
                [data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] {
                    font-size: 1.05rem !important;
                    font-weight: 800 !important;
                }

                [data-testid="stStatusWidget"] {
                    border-radius: var(--radius-md) !important;
                    border: 1px solid var(--border) !important;
                    background: var(--surface) !important;
                    box-shadow: none !important;
                    font-size: 1.05rem !important;
                }

                [data-testid="stStatusWidget"] * {
                    font-size: 1.05rem !important;
                }

                [data-testid="stAlert"] {
                    border-radius: var(--radius-md) !important;
                    border: 1px solid var(--border) !important;
                    background: #F8FAFC !important;
                    font-size: 1.05rem !important;
                }

                input, textarea, select {
                    border-radius: var(--radius-sm) !important;
                }

                a {
                    color: var(--primary-hover);
                }

                code {
                    background: #EEF2F6 !important;
                    color: var(--heading) !important;
                    border: 1px solid var(--border);
                    border-radius: 4px;
                    padding: 0.08rem 0.25rem;
                    font-size: 0.95em !important;
                }


                .table-toolbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: end;
                    gap: 1rem;
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
                    padding: 1.15rem 1.25rem;
                    margin-top: 1.25rem;
                    border-bottom: 0;
                }

                .table-title {
                    font-size: 2rem !important;
                    font-weight: 900 !important;
                    margin: 0 0 0.2rem 0 !important;
                    color: var(--heading) !important;
                }

                .table-caption {
                    font-size: 1.1rem !important;
                    color: var(--secondary) !important;
                    margin: 0 !important;
                    font-weight: 600;
                }

                div[data-testid="stVerticalBlock"] > div:has([data-testid="stDataFrame"]) {
                    margin-top: 0 !important;
                }

                @media (max-width: 1350px) {
                    .terminal-body {
                        grid-template-columns: 1fr;
                    }

                    .module-grid {
                        grid-template-columns: repeat(2, minmax(0, 1fr));
                    }

                    .workflow-strip {
                        grid-template-columns: 1fr;
                    }

                    .workflow-step {
                        border-right: 0;
                        border-bottom: 1px solid var(--border);
                    }

                    .workflow-step:last-child {
                        border-bottom: 0;
                    }
                }

                @media (max-width: 1100px) {
                    .block-container {
                        padding: 1rem 1rem 4rem 1rem !important;
                    }

                    .analysis-prep-grid {
                        grid-template-columns: 1fr;
                    }

                    .module-grid {
                        grid-template-columns: 1fr;
                    }
                }


                /* ---------------------------------------------------------
                   Final polish pass: sidebar contrast + primary actions
                   --------------------------------------------------------- */

                /* Sidebar: keep the dark analyst-control-panel direction, but
                   ensure every label, helper, selected value, and disabled state
                   remains readable. */
                [data-testid="stSidebar"] {
                    background: #0B1220 !important;
                }

                [data-testid="stSidebar"] * {
                    color: #E5EDF7 !important;
                    opacity: 1 !important;
                }

                [data-testid="stSidebar"] h1,
                [data-testid="stSidebar"] h2,
                [data-testid="stSidebar"] h3,
                [data-testid="stSidebar"] h4,
                [data-testid="stSidebar"] label {
                    color: #F8FAFC !important;
                }

                [data-testid="stSidebar"] .stCaptionContainer,
                [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
                [data-testid="stSidebar"] small,
                [data-testid="stSidebar"] p {
                    color: #CBD5E1 !important;
                    font-size: 1.02rem !important;
                    line-height: 1.45 !important;
                }

                /* Light form controls inside the dark sidebar. This fixes the
                   unreadable select/dropdown state such as the same-form value. */
                [data-testid="stSidebar"] input,
                [data-testid="stSidebar"] textarea,
                [data-testid="stSidebar"] select,
                [data-testid="stSidebar"] [data-baseweb="select"],
                [data-testid="stSidebar"] [data-baseweb="select"] > div,
                [data-testid="stSidebar"] [data-baseweb="input"],
                [data-testid="stSidebar"] [data-baseweb="base-input"],
                [data-testid="stSidebar"] [data-baseweb="textarea"] {
                    background: #F8FAFC !important;
                    border-color: #94A3B8 !important;
                    color: #0B1220 !important;
                    opacity: 1 !important;
                }

                [data-testid="stSidebar"] input *,
                [data-testid="stSidebar"] textarea *,
                [data-testid="stSidebar"] select *,
                [data-testid="stSidebar"] [data-baseweb="select"] *,
                [data-testid="stSidebar"] [data-baseweb="input"] *,
                [data-testid="stSidebar"] [data-baseweb="base-input"] *,
                [data-testid="stSidebar"] [data-baseweb="textarea"] * {
                    color: #0B1220 !important;
                    opacity: 1 !important;
                    -webkit-text-fill-color: #0B1220 !important;
                }

                [data-testid="stSidebar"] input::placeholder,
                [data-testid="stSidebar"] textarea::placeholder {
                    color: #475569 !important;
                    opacity: 1 !important;
                    -webkit-text-fill-color: #475569 !important;
                }

                [data-testid="stSidebar"] [aria-disabled="true"],
                [data-testid="stSidebar"] [disabled],
                [data-testid="stSidebar"] [aria-disabled="true"] *,
                [data-testid="stSidebar"] [disabled] * {
                    opacity: 1 !important;
                    color: #0B1220 !important;
                    -webkit-text-fill-color: #0B1220 !important;
                }

                [data-testid="stSidebar"] [role="radiogroup"] label,
                [data-testid="stSidebar"] [data-baseweb="radio"] *,
                [data-testid="stSidebar"] [data-baseweb="slider"] div,
                [data-testid="stSidebar"] [data-baseweb="slider"] span {
                    color: #E5EDF7 !important;
                    opacity: 1 !important;
                    font-size: 1.05rem !important;
                }

                /* Sidebar recommendation note. */
                [data-testid="stSidebar"] .callout {
                    background: #111B2C !important;
                    border: 1px solid #334155 !important;
                    border-left: 4px solid #5B7FA6 !important;
                    color: #E5EDF7 !important;
                    font-size: 1.02rem !important;
                    line-height: 1.5 !important;
                    padding: 1rem 1.05rem !important;
                    border-radius: var(--radius-md) !important;
                }

                [data-testid="stSidebar"] .callout,
                [data-testid="stSidebar"] .callout * {
                    color: #E5EDF7 !important;
                    opacity: 1 !important;
                }

                [data-testid="stSidebar"] .callout strong {
                    color: #FFFFFF !important;
                    font-weight: 900 !important;
                }

                [data-testid="stSidebar"] .callout code {
                    display: inline-block;
                    background: #E5EDF7 !important;
                    color: #0B1220 !important;
                    -webkit-text-fill-color: #0B1220 !important;
                    border: 1px solid #94A3B8 !important;
                    border-radius: 5px !important;
                    padding: 0.12rem 0.35rem !important;
                    font-size: 0.95em !important;
                    font-weight: 800 !important;
                    line-height: 1.2 !important;
                }

                /* Primary analysis actions: keep the button in its strong
                   institutional navy state at rest. Hover/focus should preserve
                   the same readable treatment instead of flipping into a bright
                   Streamlit-blue state. */
                .stButton > button {
                    min-height: 56px !important;
                    padding: 0.78rem 1.25rem !important;
                    border-radius: 7px !important;
                    border: 1px solid #3B5F84 !important;
                    background: #0F2742 !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    font-size: 1.12rem !important;
                    font-weight: 800 !important;
                    letter-spacing: 0 !important;
                    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.18) !important;
                    cursor: pointer !important;
                    width: 100% !important;
                }

                .stButton > button *,
                .stButton > button p,
                .stButton > button span {
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    font-size: 1.12rem !important;
                    font-weight: 800 !important;
                }

                .stButton > button:hover,
                .stButton > button:focus,
                .stButton > button:active {
                    background: #0F2742 !important;
                    border-color: #3B5F84 !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.18) !important;
                    transform: none !important;
                    cursor: pointer !important;
                }

                .stButton > button:hover *,
                .stButton > button:focus *,
                .stButton > button:active *,
                .stButton > button:hover p,
                .stButton > button:focus p,
                .stButton > button:active p,
                .stButton > button:hover span,
                .stButton > button:focus span,
                .stButton > button:active span {
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                }

                /* Keep CSV downloads secondary and readable instead of treating
                   them like primary analysis actions. */
                .stDownloadButton > button {
                    min-height: 52px !important;
                    padding: 0.7rem 1.1rem !important;
                    border-radius: 7px !important;
                    border: 1px solid #94A3B8 !important;
                    background: #FFFFFF !important;
                    color: #1E3A5F !important;
                    -webkit-text-fill-color: #1E3A5F !important;
                    font-size: 1.02rem !important;
                    font-weight: 800 !important;
                    cursor: pointer !important;
                }

                .stDownloadButton > button *,
                .stDownloadButton > button p,
                .stDownloadButton > button span {
                    color: #1E3A5F !important;
                    -webkit-text-fill-color: #1E3A5F !important;
                }

                .stDownloadButton > button:hover,
                .stDownloadButton > button:focus,
                .stDownloadButton > button:active {
                    background: #F8FAFC !important;
                    border-color: #1E3A5F !important;
                    color: #1E3A5F !important;
                    -webkit-text-fill-color: #1E3A5F !important;
                    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.10) !important;
                }

                .stDownloadButton > button:hover *,
                .stDownloadButton > button:focus *,
                .stDownloadButton > button:active * {
                    color: #1E3A5F !important;
                    -webkit-text-fill-color: #1E3A5F !important;
                }

            

                /* ---------------------------------------------------------
                   Final button color update: all Streamlit action/export
                   buttons stay dark institutional blue at rest.
                   --------------------------------------------------------- */
                .stButton > button,
                .stDownloadButton > button,
                div[data-testid="stFormSubmitButton"] > button {
                    min-height: 58px !important;
                    padding: 0.78rem 1.25rem !important;
                    border-radius: 7px !important;
                    border: 1px solid #294C73 !important;
                    background: #0F2742 !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    font-family: "Source Sans 3", system-ui, sans-serif !important;
                    font-size: 1.08rem !important;
                    font-weight: 800 !important;
                    letter-spacing: 0 !important;
                    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.18) !important;
                    cursor: pointer !important;
                    opacity: 1 !important;
                    transition: background 160ms ease-out, border-color 160ms ease-out, box-shadow 160ms ease-out !important;
                }

                .stButton > button *,
                .stButton > button p,
                .stButton > button span,
                .stDownloadButton > button *,
                .stDownloadButton > button p,
                .stDownloadButton > button span,
                div[data-testid="stFormSubmitButton"] > button *,
                div[data-testid="stFormSubmitButton"] > button p,
                div[data-testid="stFormSubmitButton"] > button span {
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    font-size: 1.08rem !important;
                    font-weight: 800 !important;
                    opacity: 1 !important;
                }

                .stButton > button:hover,
                .stButton > button:focus,
                .stButton > button:active,
                .stDownloadButton > button:hover,
                .stDownloadButton > button:focus,
                .stDownloadButton > button:active,
                div[data-testid="stFormSubmitButton"] > button:hover,
                div[data-testid="stFormSubmitButton"] > button:focus,
                div[data-testid="stFormSubmitButton"] > button:active {
                    background: #0B1F33 !important;
                    border-color: #3B5F84 !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    box-shadow: 0 3px 8px rgba(15, 23, 42, 0.22) !important;
                    transform: none !important;
                    cursor: pointer !important;
                    opacity: 1 !important;
                }

                .stButton > button:hover *,
                .stButton > button:focus *,
                .stButton > button:active *,
                .stButton > button:hover p,
                .stButton > button:focus p,
                .stButton > button:active p,
                .stButton > button:hover span,
                .stButton > button:focus span,
                .stButton > button:active span,
                .stDownloadButton > button:hover *,
                .stDownloadButton > button:focus *,
                .stDownloadButton > button:active *,
                .stDownloadButton > button:hover p,
                .stDownloadButton > button:focus p,
                .stDownloadButton > button:active p,
                .stDownloadButton > button:hover span,
                .stDownloadButton > button:focus span,
                .stDownloadButton > button:active span,
                div[data-testid="stFormSubmitButton"] > button:hover *,
                div[data-testid="stFormSubmitButton"] > button:focus *,
                div[data-testid="stFormSubmitButton"] > button:active * {
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    opacity: 1 !important;
                }

                .stButton > button:disabled,
                .stDownloadButton > button:disabled,
                div[data-testid="stFormSubmitButton"] > button:disabled,
                .stButton > button[disabled],
                .stDownloadButton > button[disabled],
                div[data-testid="stFormSubmitButton"] > button[disabled] {
                    background: #294C73 !important;
                    border-color: #294C73 !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    opacity: 0.72 !important;
                    cursor: not-allowed !important;
                }


                /* =========================================================
                   FINAL BUTTON OVERRIDE — permanent dark navy buttons
                   This is intentionally the last button rule in the file.
                   It targets Streamlit's real rendered button elements,
                   including secondary/download buttons that often look clear
                   unless overridden directly.
                   ========================================================= */

                div[data-testid="stButton"] button,
                div[data-testid="stDownloadButton"] button,
                div[data-testid="stFormSubmitButton"] button,
                .stButton button,
                .stDownloadButton button,
                button[data-testid^="baseButton"]:not([role="tab"]),
                button[data-testid^="stBaseButton"]:not([role="tab"]),
                button[kind="primary"]:not([role="tab"]),
                button[kind="secondary"]:not([role="tab"]),
                button[kind="tertiary"]:not([role="tab"]) {
                    appearance: none !important;
                    -webkit-appearance: none !important;
                    min-height: 58px !important;
                    padding: 0.82rem 1.45rem !important;
                    border-radius: 7px !important;
                    border: 1px solid #294C73 !important;
                    background: #0F2742 !important;
                    background-color: #0F2742 !important;
                    background-image: none !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    font-family: "Source Sans 3", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
                    font-size: 1.08rem !important;
                    font-weight: 800 !important;
                    line-height: 1.15 !important;
                    letter-spacing: 0 !important;
                    text-align: center !important;
                    text-decoration: none !important;
                    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.20) !important;
                    opacity: 1 !important;
                    cursor: pointer !important;
                    transition: background-color 140ms ease-out, border-color 140ms ease-out, box-shadow 140ms ease-out !important;
                }

                div[data-testid="stButton"] button *,
                div[data-testid="stButton"] button p,
                div[data-testid="stButton"] button span,
                div[data-testid="stDownloadButton"] button *,
                div[data-testid="stDownloadButton"] button p,
                div[data-testid="stDownloadButton"] button span,
                div[data-testid="stFormSubmitButton"] button *,
                div[data-testid="stFormSubmitButton"] button p,
                div[data-testid="stFormSubmitButton"] button span,
                .stButton button *,
                .stButton button p,
                .stButton button span,
                .stDownloadButton button *,
                .stDownloadButton button p,
                .stDownloadButton button span,
                button[data-testid^="baseButton"]:not([role="tab"]) *,
                button[data-testid^="baseButton"]:not([role="tab"]) p,
                button[data-testid^="baseButton"]:not([role="tab"]) span,
                button[data-testid^="stBaseButton"]:not([role="tab"]) *,
                button[data-testid^="stBaseButton"]:not([role="tab"]) p,
                button[data-testid^="stBaseButton"]:not([role="tab"]) span,
                button[kind="primary"]:not([role="tab"]) *,
                button[kind="secondary"]:not([role="tab"]) *,
                button[kind="tertiary"]:not([role="tab"]) * {
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    font-size: 1.08rem !important;
                    font-weight: 800 !important;
                    line-height: 1.15 !important;
                    text-decoration: none !important;
                    opacity: 1 !important;
                }

                div[data-testid="stButton"] button:hover,
                div[data-testid="stButton"] button:focus,
                div[data-testid="stButton"] button:focus-visible,
                div[data-testid="stButton"] button:active,
                div[data-testid="stDownloadButton"] button:hover,
                div[data-testid="stDownloadButton"] button:focus,
                div[data-testid="stDownloadButton"] button:focus-visible,
                div[data-testid="stDownloadButton"] button:active,
                div[data-testid="stFormSubmitButton"] button:hover,
                div[data-testid="stFormSubmitButton"] button:focus,
                div[data-testid="stFormSubmitButton"] button:focus-visible,
                div[data-testid="stFormSubmitButton"] button:active,
                .stButton button:hover,
                .stButton button:focus,
                .stButton button:focus-visible,
                .stButton button:active,
                .stDownloadButton button:hover,
                .stDownloadButton button:focus,
                .stDownloadButton button:focus-visible,
                .stDownloadButton button:active,
                button[data-testid^="baseButton"]:not([role="tab"]):hover,
                button[data-testid^="baseButton"]:not([role="tab"]):focus,
                button[data-testid^="baseButton"]:not([role="tab"]):focus-visible,
                button[data-testid^="baseButton"]:not([role="tab"]):active,
                button[data-testid^="stBaseButton"]:not([role="tab"]):hover,
                button[data-testid^="stBaseButton"]:not([role="tab"]):focus,
                button[data-testid^="stBaseButton"]:not([role="tab"]):focus-visible,
                button[data-testid^="stBaseButton"]:not([role="tab"]):active,
                button[kind="primary"]:not([role="tab"]):hover,
                button[kind="primary"]:not([role="tab"]):focus,
                button[kind="primary"]:not([role="tab"]):active,
                button[kind="secondary"]:not([role="tab"]):hover,
                button[kind="secondary"]:not([role="tab"]):focus,
                button[kind="secondary"]:not([role="tab"]):active,
                button[kind="tertiary"]:not([role="tab"]):hover,
                button[kind="tertiary"]:not([role="tab"]):focus,
                button[kind="tertiary"]:not([role="tab"]):active {
                    background: #162C46 !important;
                    background-color: #162C46 !important;
                    background-image: none !important;
                    border-color: #3B5F84 !important;
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    box-shadow: 0 3px 8px rgba(15, 23, 42, 0.24) !important;
                    outline: none !important;
                    transform: none !important;
                    opacity: 1 !important;
                    cursor: pointer !important;
                }

                div[data-testid="stButton"] button:hover *,
                div[data-testid="stButton"] button:focus *,
                div[data-testid="stButton"] button:active *,
                div[data-testid="stDownloadButton"] button:hover *,
                div[data-testid="stDownloadButton"] button:focus *,
                div[data-testid="stDownloadButton"] button:active *,
                div[data-testid="stFormSubmitButton"] button:hover *,
                div[data-testid="stFormSubmitButton"] button:focus *,
                div[data-testid="stFormSubmitButton"] button:active *,
                .stButton button:hover *,
                .stButton button:focus *,
                .stButton button:active *,
                .stDownloadButton button:hover *,
                .stDownloadButton button:focus *,
                .stDownloadButton button:active *,
                button[data-testid^="baseButton"]:not([role="tab"]):hover *,
                button[data-testid^="baseButton"]:not([role="tab"]):focus *,
                button[data-testid^="baseButton"]:not([role="tab"]):active *,
                button[data-testid^="stBaseButton"]:not([role="tab"]):hover *,
                button[data-testid^="stBaseButton"]:not([role="tab"]):focus *,
                button[data-testid^="stBaseButton"]:not([role="tab"]):active *,
                button[kind="primary"]:not([role="tab"]):hover *,
                button[kind="primary"]:not([role="tab"]):focus *,
                button[kind="primary"]:not([role="tab"]):active *,
                button[kind="secondary"]:not([role="tab"]):hover *,
                button[kind="secondary"]:not([role="tab"]):focus *,
                button[kind="secondary"]:not([role="tab"]):active *,
                button[kind="tertiary"]:not([role="tab"]):hover *,
                button[kind="tertiary"]:not([role="tab"]):focus *,
                button[kind="tertiary"]:not([role="tab"]):active * {
                    color: #FFFFFF !important;
                    -webkit-text-fill-color: #FFFFFF !important;
                    opacity: 1 !important;
                }

                div[data-testid="stButton"] button:disabled,
                div[data-testid="stDownloadButton"] button:disabled,
                div[data-testid="stFormSubmitButton"] button:disabled,
                .stButton button:disabled,
                .stDownloadButton button:disabled,
                button[data-testid^="baseButton"]:not([role="tab"]):disabled,
                button[data-testid^="stBaseButton"]:not([role="tab"]):disabled,
                button[kind="primary"]:not([role="tab"]):disabled,
                button[kind="secondary"]:not([role="tab"]):disabled,
                button[kind="tertiary"]:not([role="tab"]):disabled {
                    background: #294C73 !important;
                    background-color: #294C73 !important;
                    background-image: none !important;
                    border-color: #3B5F84 !important;
                    color: rgba(255, 255, 255, 0.88) !important;
                    -webkit-text-fill-color: rgba(255, 255, 255, 0.88) !important;
                    opacity: 1 !important;
                    cursor: not-allowed !important;
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
