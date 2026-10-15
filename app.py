import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.graph import SQLAgentGraph


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="SQLAgent AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Design tokens
# ============================================================

CHART_COLORWAY = [
    "#7c83f5",  # indigo
    "#7fd1c0",  # mint
    "#f5a9c0",  # blush
    "#f4cf8f",  # sand
    "#b3a4f0",  # lavender
    "#8ec3f0",  # sky
]


# ============================================================
# Ready-made examples (click -> instant result)
# ============================================================

EXAMPLES = [
    (
        "👑",
        "Top customers",
        "The 10 highest-spending customers",
        "Show me the top 10 customers by total spending",
    ),
    (
        "🌍",
        "Revenue by country",
        "Where the money comes from",
        "Show me the total revenue by country",
    ),
    (
        "🎸",
        "Popular genres",
        "Which genres sell the most tracks",
        "What are the most popular music genres?",
    ),
    (
        "🎤",
        "Best-selling artists",
        "Top 10 artists by revenue",
        "Who are the top 10 best-selling artists by total revenue?",
    ),
    (
        "📈",
        "Sales over time",
        "Total revenue for each year",
        "Show me the total revenue for each year",
    ),
    (
        "🎧",
        "Top tracks",
        "The 10 most purchased tracks",
        "What are the 10 most purchased tracks?",
    ),
]


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #fafaff;
        --card: #ffffff;
        --soft: #f3f4ff;
        --border: #ebedf8;
        --border-strong: #dcdff5;
        --text: #25283d;
        --text-soft: #6a7090;
        --text-faint: #9ba0bd;
        --accent: #6f7df0;
        --accent-deep: #5562e4;
        --accent-soft: #eef0ff;
        --shadow-sm: 0 1px 3px rgba(60, 70, 140, 0.05), 0 4px 14px rgba(60, 70, 140, 0.04);
        --shadow-md: 0 12px 34px rgba(60, 70, 140, 0.09);
    }

    html, body, .stApp, .stMarkdown, button, input, textarea {
        font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(900px 480px at 88% -8%, #eaecff 0%, transparent 60%),
            radial-gradient(800px 480px at -8% 6%, #e9f8f3 0%, transparent 55%),
            var(--bg);
        color: var(--text);
    }

    .main .block-container {
        max-width: 1080px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* ---------- Hero ---------- */
    .hero {
        text-align: center;
        padding: 1.2rem 0 1.6rem 0;
    }
    .hero-pill {
        display: inline-block;
        background: var(--accent-soft);
        color: var(--accent-deep);
        border: 1px solid var(--border-strong);
        border-radius: 999px;
        padding: 0.28rem 0.85rem;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.9rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        line-height: 1.1;
        color: var(--text);
        margin-bottom: 0.7rem;
    }
    .hero-title span {
        background: linear-gradient(120deg, #6f7df0 0%, #5cc7b2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .hero-description {
        font-size: 1.04rem;
        color: var(--text-soft);
        line-height: 1.7;
        max-width: 620px;
        margin: 0 auto;
    }

    /* ---------- Section headings ---------- */
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        margin: 2rem 0 0.2rem 0;
    }
    .section-sub {
        font-size: 0.86rem;
        color: var(--text-faint);
        margin-bottom: 0.9rem;
    }

    /* ---------- Ask box (form) ---------- */
    [data-testid="stForm"] {
        background: var(--card);
        border: 1px solid var(--border) !important;
        border-radius: 22px;
        padding: 0.7rem 0.8rem !important;
        box-shadow: var(--shadow-md);
    }
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"] input {
        font-size: 1.04rem;
        color: var(--text);
        padding: 0.7rem 0.6rem;
    }
    div[data-baseweb="input"] input::placeholder {
        color: var(--text-faint);
    }

    /* ---------- Primary button ---------- */
    button[kind="primaryFormSubmit"],
    button[kind="primary"],
    button[data-testid="stBaseButton-primaryFormSubmit"],
    button[data-testid="stBaseButton-primary"] {
        width: 100%;
        border-radius: 14px;
        border: none;
        background: linear-gradient(135deg, #7f8cf3 0%, #6573ea 100%);
        color: #fff;
        font-weight: 700;
        padding: 0.7rem 1.2rem;
        box-shadow: 0 8px 20px rgba(101, 115, 234, 0.28);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    button[kind="primaryFormSubmit"]:hover,
    button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primaryFormSubmit"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        color: #fff;
        border: none;
        transform: translateY(-1px);
        box-shadow: 0 12px 26px rgba(101, 115, 234, 0.36);
    }

    /* ---------- Example cards ---------- */
    [class*="st-key-ex_"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1.05rem 1.15rem 0.5rem 1.15rem;
        box-shadow: var(--shadow-sm);
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }
    [class*="st-key-ex_"]:hover {
        transform: translateY(-3px);
        border-color: var(--border-strong);
        box-shadow: var(--shadow-md);
    }
    .ex-icon {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        background: var(--accent-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-bottom: 0.65rem;
    }
    .ex-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: var(--text);
    }
    .ex-desc {
        font-size: 0.84rem;
        color: var(--text-soft);
        margin: 0.15rem 0 0.35rem 0;
    }
    [class*="st-key-ex_"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--accent-deep) !important;
        font-weight: 700;
        font-size: 0.86rem;
        padding: 0.2rem 0 !important;
        min-height: 0;
    }
    [class*="st-key-ex_"] button:hover {
        color: var(--accent) !important;
        transform: translateX(3px);
    }

    /* ---------- Answer card ---------- */
    .st-key-answer_card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1.4rem 1.6rem;
        box-shadow: var(--shadow-md);
        margin-bottom: 1rem;
    }
    .st-key-answer_card p,
    .st-key-answer_card li {
        font-size: 1.02rem;
        line-height: 1.75;
        color: var(--text);
    }
    .st-key-answer_card table {
        width: auto;
        border-collapse: separate;
        border-spacing: 0;
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .st-key-answer_card th,
    .st-key-answer_card td {
        border: none;
        border-bottom: 1px solid var(--border);
        padding: 0.55rem 1rem;
    }
    .st-key-answer_card th {
        background: var(--soft);
        color: var(--text);
        font-weight: 600;
    }
    .answer-label {
        color: var(--accent);
        font-weight: 700;
        font-size: 0.74rem;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    .asked {
        color: var(--text-soft);
        font-size: 0.9rem;
        margin: 1.8rem 0 0.7rem 0;
    }
    .asked b {
        color: var(--text);
    }

    /* ---------- Stat chips ---------- */
    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.2rem 0 1rem 0;
    }
    .chip {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 0.32rem 0.85rem;
        font-size: 0.8rem;
        color: var(--text-soft);
        font-weight: 500;
    }
    .chip b {
        color: var(--accent-deep);
        font-weight: 700;
    }

    /* ---------- Tabs ---------- */
    button[data-baseweb="tab"] {
        font-weight: 600;
        color: var(--text-soft);
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-deep);
    }
    div[data-baseweb="tab-highlight"] {
        background-color: var(--accent) !important;
    }

    /* ---------- Data, code, charts ---------- */
    pre {
        border-radius: 14px !important;
        border: 1px solid var(--border) !important;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
    }
    div[data-testid="stPlotlyChart"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0.5rem;
    }
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }
    .stDownloadButton button {
        border-radius: 12px;
        border: 1px solid var(--border-strong);
        background: var(--card);
        color: var(--accent-deep);
        font-weight: 600;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: #fcfcff;
        border-right: 1px solid var(--border);
    }
    .sb-brand {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--text);
    }
    .sb-sub {
        font-size: 0.82rem;
        color: var(--text-faint);
        margin-bottom: 1.2rem;
    }
    .sb-card {
        background: var(--soft);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.9rem;
    }
    .sb-title {
        color: var(--accent-deep);
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.35rem;
    }
    .sb-item {
        color: var(--text-soft);
        font-size: 0.84rem;
        margin: 0.3rem 0;
    }

    /* ---------- Chrome ---------- */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: rgba(250, 250, 255, 0.7) !important;
        backdrop-filter: blur(12px);
    }

    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.4rem;
        border-top: 1px solid var(--border);
        color: var(--text-faint);
        font-size: 0.8rem;
    }

    @media (max-width: 640px) {
        .hero-title { font-size: 2.1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Agent
# ============================================================

@st.cache_resource
def load_agent(provider="groq"):
    return SQLAgentGraph(provider=provider)


# Groq is the primary provider; Gemini is the automatic fallback.
agent = load_agent("groq")


# ============================================================
# Session state
# ============================================================

defaults = {
    "question_input": "",
    "pending": None,    # question waiting to be executed
    "last": None,       # last displayed result
    "cache": {},        # question -> result (repeat clicks are instant)
    "empty_warning": False,
    "scroll": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def pick_example(query):
    """Example clicked: fill the box and run immediately."""
    st.session_state.question_input = query
    st.session_state.pending = query


def submit_question():
    """Run button / Enter pressed."""
    query = st.session_state.question_input.strip()
    if query:
        st.session_state.pending = query
    else:
        st.session_state.empty_warning = True


def style_chart(fig):
    """Soft, light look for Plotly charts."""
    try:
        fig.update_layout(
            colorway=CHART_COLORWAY,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#4a5070"),
            title_font=dict(size=16, color="#25283d"),
            margin=dict(l=20, r=20, t=60, b=20),
            barcornerradius=8,
        )
    except Exception:
        pass
    try:
        fig.update_xaxes(gridcolor="#eceefa", linecolor="#e1e4f5", zeroline=False)
        fig.update_yaxes(gridcolor="#eceefa", linecolor="#e1e4f5", zeroline=False)
        fig.update_traces(
            marker_color=CHART_COLORWAY[0],
            marker_line_width=0,
            selector=dict(type="bar"),
        )
    except Exception:
        pass
    return fig


# ============================================================
# Sidebar (kept minimal)
# ============================================================

with st.sidebar:
    st.markdown('<div class="sb-brand">✨ SQLAgent AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-sub">Autonomous Text-to-SQL Analytics</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="sb-card">
            <div class="sb-title">🔐 Security</div>
            <div class="sb-item">✓ Read-only database access</div>
            <div class="sb-item">✓ SELECT / WITH queries only</div>
            <div class="sb-item">✓ SQL validation with sqlglot</div>
        </div>
        <div class="sb-card">
            <div class="sb-title">⚙️ Agent</div>
            <div class="sb-item">✓ Natural language → SQL</div>
            <div class="sb-item">✓ Automatic SQL correction</div>
            <div class="sb-item">✓ Summaries &amp; charts</div>
            <div class="sb-item">✓ LangGraph orchestration</div>
        </div>
        <div class="sb-card">
            <div class="sb-title">🗄️ Database</div>
            <div class="sb-item">SQLite · Chinook · 11 tables</div>
        </div>
        <div class="sb-card">
            <div class="sb-title">🧠 LLM</div>
            <div class="sb-item">Primary: Groq</div>
            <div class="sb-item">Automatic fallback: Gemini</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Hero
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-pill">✨ Text-to-SQL · Chinook music store</div>
        <div class="hero-title">Ask your data <span>anything</span></div>
        <div class="hero-description">
            Type a question in plain English. SQLAgent writes safe SQL,
            runs it read-only, explains the answer and draws a chart
            when it helps.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Ask box
# ============================================================

with st.form("ask_form", border=False):
    col_input, col_btn = st.columns([5, 1.3], vertical_alignment="center")
    with col_input:
        st.text_input(
            "Question",
            placeholder="Ask something, e.g. Show me the top 10 customers by total spending",
            label_visibility="collapsed",
            key="question_input",
        )
    with col_btn:
        st.form_submit_button(
            "Ask  →",
            type="primary",
            on_click=submit_question,
        )

if st.session_state.empty_warning:
    st.session_state.empty_warning = False
    st.warning("Please type a question first, or pick one of the examples below.")


# ============================================================
# Examples
# ============================================================

st.markdown(
    """
    <div class="section-title">Try an example</div>
    <div class="section-sub">One click — the answer appears instantly.</div>
    """,
    unsafe_allow_html=True,
)

for row_start in range(0, len(EXAMPLES), 3):
    cols = st.columns(3)
    for col, (idx, (icon, title, desc, query)) in zip(
        cols,
        list(enumerate(EXAMPLES))[row_start:row_start + 3],
    ):
        with col:
            with st.container(key=f"ex_{idx}"):
                st.markdown(
                    f"""
                    <div class="ex-icon">{icon}</div>
                    <div class="ex-title">{title}</div>
                    <div class="ex-desc">{desc}</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.button(
                    "Show result →",
                    key=f"ex_btn_{idx}",
                    on_click=pick_example,
                    args=(query,),
                )


# ============================================================
# Execute pending question
# ============================================================

pending = st.session_state.pending

if pending:
    st.session_state.pending = None
    cache = st.session_state.cache

    if pending in cache:
        st.session_state.last = {"question": pending, "result": cache[pending], "error": None}
        st.session_state.scroll = True
    else:
        with st.spinner("✨ Thinking, writing SQL and checking the results..."):
            try:
                outcome = agent.run(pending)
                cache[pending] = outcome
                st.session_state.last = {"question": pending, "result": outcome, "error": None}
            except Exception as exc:
                st.session_state.last = {"question": pending, "result": None, "error": str(exc)}
        st.session_state.scroll = True


# ============================================================
# Results
# ============================================================

last = st.session_state.last

if last:

    st.markdown('<div id="results-anchor"></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="asked">You asked: <b>{last["question"]}</b></div>',
        unsafe_allow_html=True,
    )

    if last["error"]:
        st.error("The agent could not complete this request. Please try rephrasing your question.")
        with st.expander("Technical details"):
            st.code(last["error"])

    else:
        result = last["result"]
        rows = result["result"] or []
        has_chart = bool(result.get("should_chart")) and result.get("chart") is not None

        # ----- Answer -----
        with st.container(key="answer_card"):
            st.markdown('<div class="answer-label">AI ANALYSIS</div>', unsafe_allow_html=True)
            st.markdown(result["answer"])

        # ----- Quick stats -----
        attempts = result["attempts"]
        st.markdown(
            f"""
            <div class="chips">
                <span class="chip"><b>{len(rows)}</b> rows</span>
                <span class="chip"><b>{attempts}</b> SQL attempt{'s' if attempts != 1 else ''}</span>
                <span class="chip">Chart: <b>{'yes' if has_chart else 'not needed'}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----- Details in tabs -----
        tab_names = (["📈 Chart"] if has_chart else []) + ["🗂 Data", "🧠 SQL"]
        tabs = st.tabs(tab_names)
        tab_iter = iter(tabs)

        if has_chart:
            with next(tab_iter):
                st.plotly_chart(
                    style_chart(result["chart"]),
                    use_container_width=True,
                    theme=None,
                )

        with next(tab_iter):
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇ Download CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="query_results.csv",
                    mime="text/csv",
                )
            else:
                st.info("The query returned no rows.")

        with next(tab_iter):
            st.code(result["sql"], language="sql")

    # Smoothly bring the fresh result into view
    if st.session_state.scroll:
        st.session_state.scroll = False
        components.html(
            """
            <script>
            const el = window.parent.document.getElementById('results-anchor');
            if (el) { el.scrollIntoView({behavior: 'smooth', block: 'start'}); }
            </script>
            """,
            height=0,
        )


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div class="footer">
        SQLAgent AI · Python · LangGraph · Gemini · Groq · SQLite · Plotly
    </div>
    """,
    unsafe_allow_html=True,
)
