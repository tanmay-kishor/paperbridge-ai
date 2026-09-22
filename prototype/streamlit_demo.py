"""
PaperBridge AI - Internal Streamlit Prototype & Viva Demonstration Tool
(Reference: Section 7 - Dev-time Prototyping)

This interactive tool allows rapid testing and demonstration of the PaperBridge AI
pipeline during internal team check-ins and academic viva presentations.
"""

import sys
import os

# Ensure backend modules can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from backend.pipeline.ranker import run_pipeline

st.set_page_config(
    page_title="PaperBridge AI - Prototype",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 PaperBridge AI — Pipeline Prototype")
st.markdown(
    "**Core Demonstration:** Semantic Retrieval, Open-Access Verification, "
    "Paywall Fallback, and Reading Difficulty Profiling."
)

# Sidebar: Controls and Viva Explanations
with st.sidebar:
    st.header("⚙️ Search Controls")
    mode = st.radio(
        "Search Mode:",
        options=["topic", "paper"],
        format_func=lambda x: "By Research Topic" if x == "topic" else "By Paper Title / DOI"
    )
    limit = st.slider("Result Limit:", min_value=1, max_value=15, value=5)

    st.markdown("---")
    st.header("💡 Viva / Evaluation Quick-Picks")
    if st.button("Transformer Time-Series"):
        st.session_state["query_input"] = "transformer models for time series forecasting"
        st.session_state["mode_select"] = "topic"
    if st.button("Paywalled DOI Fallback"):
        st.session_state["query_input"] = "10.1145/3318464.3389700"
        st.session_state["mode_select"] = "paper"
    if st.button("Quantum Key Distribution"):
        st.session_state["query_input"] = "quantum key distribution protocols security"
        st.session_state["mode_select"] = "topic"

# Query Input
default_query = st.session_state.get("query_input", "transformer models for time series forecasting")
query = st.text_input("Enter Topic, Title, or DOI:", value=default_query)

if st.button("Run Recommendation Pipeline", type="primary"):
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Executing pipeline: Semantic Scholar -> SentenceTransformer -> Unpaywall -> Readability..."):
            response = run_pipeline(query=query, mode=mode, limit=limit)

        paywalled_original = response.get("paywalled_original")
        if paywalled_original:
            st.warning(
                f"🚨 **Paywall Fallback Triggered!**\n\n"
                f"The requested publication *'{paywalled_original.get('title')}'* (DOI: {paywalled_original.get('doi')}) "
                f"is paywalled. The pipeline has automatically surfaced the closest legitimate, open-access alternatives below."
            )

        results = response.get("results", [])
        st.subheader(f"Ranked Recommendations ({len(results)} papers)")

        for i, paper in enumerate(results):
            diff = paper.get("difficulty", {})
            diff_level = diff.get("level", "Intermediate")
            badge_color = "🟢" if diff_level == "Foundational" else "🟡" if diff_level == "Intermediate" else "🟣"
            oa_badge = "🔓 Free Open-Access PDF" if paper.get("is_open_access") else "🔒 Paywalled"

            with st.expander(f"#{i+1}: {paper.get('title')} ({int(round(paper.get('relevance_score', 0)*100))}% Match | {badge_color} {diff_level} | {oa_badge})", expanded=(i == 0)):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**Authors:** {', '.join(paper.get('authors', []))}")
                    st.markdown(f"**Venue / Year:** {paper.get('venue') or 'N/A'} ({paper.get('year') or 'N/A'})")
                    st.markdown(f"**Abstract:** {paper.get('abstract') or 'No abstract available.'}")
                    st.info(f"**Why Recommended:** {paper.get('why_recommended')}")

                with cols[1]:
                    st.metric("Semantic Match", f"{int(round(paper.get('relevance_score', 0)*100))}%")
                    st.metric("Reading Grade (FKGL)", f"Grade {diff.get('fk_grade', 'N/A')}")
                    st.metric("Jargon Density", f"{diff.get('jargon_density', 'N/A')}")
                    st.metric("Citations", f"{paper.get('citation_count', 0):,}")

                    if paper.get("oa_url"):
                        st.markdown(f"[📥 **Download Free PDF**]({paper.get('oa_url')})")
                    if paper.get("doi"):
                        st.caption(f"DOI: {paper.get('doi')}")

st.markdown("---")
st.caption("PaperBridge AI Prototype | B.Tech Mini-Project | Meets all Section 4.1 Core Specifications")
