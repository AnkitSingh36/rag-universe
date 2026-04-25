"""
Shared CSS design system for RAG Master Guide.
Import and call apply_global_styles() at the top of each page.
"""

import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:ital,wght@0,400;0,600;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── HIDE STREAMLIT CHROME ─────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stDecoration"] {display: none;}

/* ── BUTTON OVERRIDES ──────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 25px rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    color: #818cf8 !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(99,102,241,0.16) !important;
    border-color: rgba(99,102,241,0.45) !important;
}

/* ── METRIC CARDS ──────────────────────────────────────── */
[data-testid="metric-container"] {
    background: rgba(13,21,38,0.9) !important;
    border: 1px solid rgba(99,102,241,0.13) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.2rem !important;
    transition: all 0.2s !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(99,102,241,0.35) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.1) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #F0F4FF !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: #8892A4 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    font-weight: 600 !important;
}

/* ── SIDEBAR ───────────────────────────────────────────── */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(175deg, #060D1C 0%, #0A1628 60%, #0D1A30 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.13) !important;
}

/* ── TABS ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(5,11,24,0.8) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #8892A4 !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.18) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
}

/* ── EXPANDERS ─────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: rgba(13,21,38,0.8) !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    font-weight: 600 !important;
    color: #c7d2fe !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(99,102,241,0.3) !important;
    background: rgba(17,24,39,0.9) !important;
}
.streamlit-expanderContent {
    background: rgba(9,15,27,0.6) !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── TEXT INPUTS ───────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(13,21,38,0.9) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    color: #F0F4FF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* ── SELECT BOX ────────────────────────────────────────── */
.stSelectbox > div > div > div {
    background: rgba(13,21,38,0.9) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    color: #F0F4FF !important;
}

/* ── PROGRESS BAR ──────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899) !important;
    border-radius: 99px !important;
}

/* ── ALERTS ────────────────────────────────────────────── */
.stSuccess > div {
    background: rgba(16,185,129,0.07) !important;
    border: 1px solid rgba(16,185,129,0.22) !important;
    border-radius: 10px !important;
    color: #a7f3d0 !important;
}
.stWarning > div {
    background: rgba(245,158,11,0.07) !important;
    border: 1px solid rgba(245,158,11,0.22) !important;
    border-radius: 10px !important;
    color: #fde68a !important;
}
.stError > div {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.22) !important;
    border-radius: 10px !important;
    color: #fca5a5 !important;
}
.stInfo > div {
    background: rgba(99,102,241,0.07) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    border-radius: 10px !important;
    color: #c7d2fe !important;
}

/* ── DATAFRAME ─────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── CODE BLOCKS ───────────────────────────────────────── */
.stCode {
    border-radius: 12px !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
}

/* ── RADIO BUTTONS ─────────────────────────────────────── */
.stRadio label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}

/* ─────────────────────────────────────────────────────── */
/* CUSTOM COMPONENT CLASSES                                */
/* ─────────────────────────────────────────────────────── */

/* Hero */
.hero-wrap {
    padding: 2.8rem 1.5rem 2rem;
    text-align: center;
    background: radial-gradient(ellipse at 50% -10%, rgba(99,102,241,0.1) 0%, transparent 60%);
    border-radius: 20px;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(99,102,241,0.07);
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 999px;
    padding: 0.3rem 1rem;
    font-size: 0.7rem;
    font-weight: 700;
    color: #818cf8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    line-height: 1.12;
    background: linear-gradient(135deg, #c7d2fe 0%, #818cf8 30%, #a855f7 60%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0.3rem 0 0.8rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: #8892A4;
    max-width: 560px;
    margin: 0 auto 0;
    line-height: 1.7;
    font-weight: 400;
}

/* Section header */
.sec-head { margin: 2.2rem 0 1.2rem; }
.sec-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.3rem;
}
.sec-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #F0F4FF;
    line-height: 1.3;
}

/* G-card (generic elevated card) */
.g-card {
    background: linear-gradient(145deg, rgba(13,21,38,0.95), rgba(9,15,27,0.9));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.25s ease;
    height: 100%;
}
.g-card:hover {
    border-color: rgba(99,102,241,0.35);
    box-shadow: 0 8px 32px rgba(99,102,241,0.1);
    transform: translateY(-2px);
}

/* Learning path step card */
.lp-card {
    background: linear-gradient(155deg, rgba(17,24,39,0.98), rgba(9,15,27,0.95));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 1.8rem 1.4rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
    position: relative;
    overflow: hidden;
    min-height: 220px;
}
.lp-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 50% -10%, rgba(99,102,241,0.07), transparent 55%);
    pointer-events: none;
}
.lp-card:hover {
    border-color: rgba(99,102,241,0.4);
    box-shadow: 0 16px 50px rgba(99,102,241,0.15), 0 0 0 1px rgba(99,102,241,0.1);
    transform: translateY(-6px);
}
.lp-bg-num {
    position: absolute;
    top: 0.8rem; right: 1rem;
    font-size: 3.5rem;
    font-weight: 900;
    color: rgba(99,102,241,0.06);
    line-height: 1;
    pointer-events: none;
}
.lp-emoji { font-size: 2rem; display: block; margin-bottom: 0.7rem; position: relative; z-index: 1; }
.lp-title { font-size: 0.92rem; font-weight: 700; color: #F0F4FF; margin-bottom: 0.45rem; position: relative; z-index: 1; }
.lp-desc { font-size: 0.8rem; color: #8892A4; line-height: 1.55; position: relative; z-index: 1; }
.lp-cta {
    display: inline-block; margin-top: 0.9rem;
    padding: 0.3rem 0.85rem;
    font-size: 0.72rem; font-weight: 600;
    color: #818cf8;
    background: rgba(99,102,241,0.09);
    border: 1px solid rgba(99,102,241,0.22);
    border-radius: 6px;
    position: relative; z-index: 1;
}

/* Info box */
.info-box {
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.18);
    border-left: 3px solid #6366f1;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin: 1rem 0;
    color: #c7d2fe;
    font-size: 0.91rem;
    line-height: 1.65;
}

/* Divider */
.fancy-div {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.22), transparent);
    margin: 1.8rem 0;
}

/* Pipeline flow */
.pipeline-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0;
    margin: 1.2rem 0;
    padding: 1.5rem 1rem;
    background: rgba(5,11,24,0.7);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 16px;
}
.pipe-box {
    background: linear-gradient(145deg, rgba(17,24,39,0.97), rgba(9,15,27,0.95));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
    min-width: 88px;
    transition: all 0.2s;
}
.pipe-box:hover {
    border-color: rgba(99,102,241,0.4);
    box-shadow: 0 4px 16px rgba(99,102,241,0.12);
    transform: translateY(-2px);
}
.pipe-icon { font-size: 1.5rem; display: block; margin-bottom: 3px; }
.pipe-lbl { font-size: 0.62rem; color: #6366f1; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; }
.pipe-nm { font-size: 0.78rem; color: #e2e8f0; font-weight: 600; margin-top: 2px; }
.pipe-arr { font-size: 1.3rem; color: rgba(99,102,241,0.6); padding: 0 0.35rem; }

/* Answer result box */
.ans-box {
    background: linear-gradient(135deg, rgba(6,78,59,0.25), rgba(2,44,34,0.35));
    border: 1px solid rgba(16,185,129,0.28);
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
}
.ans-label {
    font-size: 0.67rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #34d399; margin-bottom: 0.55rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.ans-text { font-size: 0.97rem; color: #e2e8f0; line-height: 1.7; }

/* Chunk retrieval card */
.chunk-card {
    background: rgba(13,21,38,0.8);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin: 0.45rem 0;
    transition: all 0.15s;
}
.chunk-card:hover {
    background: rgba(17,27,50,0.9);
}

/* Pipeline log */
.log-item {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    margin: 0.4rem 0;
    padding: 0.55rem 0.7rem;
    background: rgba(9,15,27,0.7);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.04);
}
.log-n {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 50%;
    min-width: 22px; height: 22px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
}
.log-sname { color: #e2e8f0; font-size: 0.83rem; font-weight: 600; }
.log-sdetail { color: #8892A4; font-size: 0.77rem; margin-top: 1px; }

/* Comparison stats card */
.cmp-card {
    background: rgba(13,21,38,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
}

/* Badge */
.bdg {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.bdg-green { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
.bdg-amber { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
.bdg-red { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.bdg-purple { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
.bdg-blue { background: rgba(59,130,246,0.12); color: #60a5fa; border: 1px solid rgba(59,130,246,0.2); }

/* Encyclopedia overview card */
.enc-card {
    border-radius: 12px;
    padding: 0.9rem 0.75rem;
    text-align: center;
    margin: 4px 0;
    min-height: 88px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    cursor: default;
}
.enc-card:hover {
    transform: translateY(-2px);
}
.enc-emoji { font-size: 1.4rem; margin-bottom: 0.25rem; }
.enc-name { font-size: 0.78rem; font-weight: 700; color: #F0F4FF; }
.enc-meta { font-size: 0.67rem; color: #8892A4; margin-top: 2px; }

/* Scenario card */
.sc-card {
    background: rgba(13,21,38,0.9);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin: 0.35rem 0;
    transition: all 0.2s;
}
.sc-card:hover { border-color: rgba(99,102,241,0.3); }

/* Sidebar page link styling override */
.stPageLink > a {
    border-radius: 8px !important;
    padding: 0.35rem 0.6rem !important;
    transition: all 0.15s !important;
}
.stPageLink > a:hover {
    background: rgba(99,102,241,0.1) !important;
}
</style>
"""


def apply_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def sidebar_nav(current_page: str = ""):
    """Render consistent sidebar navigation."""
    with st.sidebar:
        st.markdown("""
<div style="padding:0.4rem 0 1rem">
  <div style="font-size:1.05rem;font-weight:800;background:linear-gradient(135deg,#818cf8,#a855f7);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    🧠 RAG Master Guide
  </div>
  <div style="font-size:0.72rem;color:#4A5568;margin-top:0.2rem;font-weight:500;letter-spacing:0.05em;text-transform:uppercase">
    Learn • Explore • Build
  </div>
</div>
""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6366f1;margin-bottom:0.5rem">Navigation</div>', unsafe_allow_html=True)

        pages = [
            ("app.py", "🏠", "Home"),
            ("pages/1_When_To_Use_RAG.py", "1️⃣", "When To Use RAG"),
            ("pages/2_How_RAG_Works.py", "2️⃣", "How RAG Works"),
            ("pages/3_Test_Any_RAG.py", "⭐", "Test Any RAG"),
            ("pages/4_Compare_RAGs.py", "4️⃣", "Compare RAGs"),
            ("pages/5_RAG_Encyclopedia.py", "📖", "Encyclopedia"),
            ("pages/6_Build_Your_Own.py", "🛠️", "Build Your Own"),
        ]

        for path, icon, label in pages:
            star = " ⭐" if path == "pages/3_Test_Any_RAG.py" and current_page != "3" else ""
            st.page_link(path, label=f"{icon} {label}{star}")
