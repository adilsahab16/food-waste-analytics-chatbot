import os
import sys
from pathlib import Path

# Ensure repo root is on the path so 'src' is importable on Streamlit Cloud
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv
from src.agent import run_agent

load_dotenv()

# ── Database bootstrap ────────────────────────────────────────────────────────
# On Streamlit Cloud, db/ is gitignored and never committed.
# Build the database from sample data on first run if it doesn't exist.

_DB_PATH = Path(__file__).resolve().parent.parent / 'db' / 'food_waste.db'
if not _DB_PATH.exists():
    from src.load_data import main as _build_db
    _build_db()

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Food Waste Analytics",
    page_icon="🌍",
    layout="centered",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Food Waste Analytics")
    st.caption("World Food Loss & GHG Emissions Explorer")

    st.divider()

    # Data mode indicator
    data_mode = os.environ.get("DATA_MODE", "full").lower()
    if data_mode == "sample":
        st.info("**Data mode:** Demo (sample data)", icon="📊")
    else:
        st.success("**Data mode:** Full dataset", icon="📊")

    st.divider()

    st.markdown("**Data Sources**")
    st.markdown(
        """
- **FAO** — Food loss & waste percentages, food system emissions
- **WDI** — World Bank population and GDP data
- **PIK** — Total economy-wide GHG emissions by sector
- **EDGAR** — Food system share of total GHG emissions
        """
    )

    st.divider()

    st.markdown("**About**")
    st.markdown(
        """
This chatbot answers natural language questions over structured food
waste and emissions data covering 1966–2022.

Built as a learning & portfolio project using the Anthropic API,
Python, SQLite, and Streamlit.
        """
    )

# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Main area ─────────────────────────────────────────────────────────────────

st.header("Food Waste & Emissions Chat")

# Conversation starter cards — shown only when chat is empty
STARTER_QUESTIONS = [
    "How has food loss changed over time in high vs low income regions?",
    "Which supply chain stage has the highest food loss by region?",
    "What share of total GHG emissions comes from the food system, by region?",
    "Compare crop vs livestock emissions across regions.",
]

if not st.session_state.messages:
    st.markdown("##### Ask a question or choose one to get started:")
    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]
    for i, question in enumerate(STARTER_QUESTIONS):
        if cols[i].button(question, key=f"starter_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────

if prompt := st.chat_input("Ask about food loss or emissions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# Run agent if the last message is from the user and has no response yet
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_question = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(user_question)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
