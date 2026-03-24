import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

from analyzer import analyze_website
from monitor import run_monitoring_cycle
from database import (
    init_db,
    save_analysis,
    get_all_analyses,
    add_monitored_site,
    get_monitored_sites,
    toggle_site_status,
    delete_site_completely
)

st.set_page_config(
    page_title="DarkLens · Pattern Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0B0E14;
    color: #D6DCE8;
}
.main .block-container {
    padding: 2.4rem 2.8rem 3rem 2.8rem;
    max-width: 1280px;
}
[data-testid="stSidebar"] {
    background: #0F1219;
    border-right: 1px solid #1E2332;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.2rem; }
.sidebar-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0 0.4rem 2rem 0.4rem;
    border-bottom: 1px solid #1E2332; margin-bottom: 1.6rem;
}
.sidebar-brand-icon { font-size: 1.6rem; line-height: 1; }
.sidebar-brand-name {
    font-family: 'Syne', sans-serif; font-weight: 800;
    font-size: 1.25rem; color: #E8ECF5; letter-spacing: -0.02em;
}
.sidebar-brand-sub {
    font-size: 0.65rem; font-weight: 400; color: #5A6278;
    letter-spacing: 0.08em; text-transform: uppercase;
}
[data-testid="stRadio"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important; color: #7A84A0 !important;
    padding: 0.5rem 0.8rem !important; border-radius: 8px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stRadio"] label:hover {
    color: #D6DCE8 !important; background: #161B26 !important;
}
[data-testid="stRadio"] [data-checked="true"] label {
    color: #61AFEF !important; background: #161B26 !important; font-weight: 500 !important;
}
.page-header { margin-bottom: 2rem; }
.page-title {
    font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 800;
    color: #E8ECF5; letter-spacing: -0.03em; margin: 0 0 0.25rem 0;
}
.page-subtitle { font-size: 0.875rem; color: #5A6278; margin: 0; }
.card {
    background: #131720; border: 1px solid #1E2332;
    border-radius: 14px; padding: 1.5rem 1.75rem; margin-bottom: 1.25rem;
}
.risk-low {
    background: linear-gradient(135deg, #0D2818 0%, #0F1E12 100%);
    border: 1px solid #1B4D30; border-left: 4px solid #2ECC71;
    border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.5rem;
}
.risk-moderate {
    background: linear-gradient(135deg, #261E0A 0%, #1E1808 100%);
    border: 1px solid #5C440E; border-left: 4px solid #F39C12;
    border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.5rem;
}
.risk-high {
    background: linear-gradient(135deg, #280D0D 0%, #1E0A0A 100%);
    border: 1px solid #5C1818; border-left: 4px solid #E74C3C;
    border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.5rem;
}
.risk-label {
    font-family: 'DM Mono', monospace; font-size: 0.75rem; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
}
.risk-low .risk-label  { color: #2ECC71; }
.risk-moderate .risk-label { color: #F39C12; }
.risk-high .risk-label { color: #E74C3C; }
.risk-description { font-size: 0.83rem; color: #7A84A0; margin-top: 0.2rem; }
.metric-card {
    background: #131720; border: 1px solid #1E2332;
    border-radius: 12px; padding: 1.2rem 1.4rem; text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif; font-size: 2.4rem; font-weight: 800;
    color: #E8ECF5; line-height: 1; margin-bottom: 0.35rem;
}
.metric-label {
    font-size: 0.75rem; color: #5A6278;
    text-transform: uppercase; letter-spacing: 0.1em;
}
.section-label {
    font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.14em; text-transform: uppercase; color: #5A6278;
    margin-bottom: 0.9rem; padding-bottom: 0.5rem; border-bottom: 1px solid #1E2332;
}
.hr { border: none; border-top: 1px solid #1E2332; margin: 1.8rem 0; }
[data-testid="stExpander"] {
    background: #131720 !important; border: 1px solid #1E2332 !important;
    border-radius: 10px !important; margin-bottom: 0.6rem !important;
}
[data-testid="stExpander"] summary { font-size: 0.875rem !important; color: #C0C8DC !important; }
[data-testid="stTextInput"] input {
    background: #131720 !important; border: 1px solid #2A3044 !important;
    border-radius: 9px !important; color: #D6DCE8 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #61AFEF !important; box-shadow: 0 0 0 2px rgba(97,175,239,0.15) !important;
}
[data-testid="stButton"] > button {
    background: #1A2035 !important; border: 1px solid #2A3650 !important;
    border-radius: 9px !important; color: #A0AECB !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.875rem !important;
    font-weight: 500 !important; padding: 0.5rem 1.2rem !important;
    transition: all 0.15s ease !important;
}
[data-testid="stButton"] > button:hover {
    background: #223058 !important; border-color: #61AFEF !important; color: #E8ECF5 !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid #1E2332 !important; border-radius: 12px !important; overflow: hidden !important;
}
[data-testid="stAlert"] { border-radius: 10px !important; font-size: 0.875rem !important; }
.token-chip {
    display: inline-block; background: #1A2035; border: 1px solid #2A3044;
    border-radius: 6px; padding: 0.15rem 0.5rem;
    font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #7A90BC;
    margin: 0.15rem 0.2rem 0.15rem 0;
}
.badge-active {
    background: #0D2818; border: 1px solid #1B4D30; color: #2ECC71;
    font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.2rem 0.6rem; border-radius: 20px; font-family: 'DM Mono', monospace;
}
.badge-inactive {
    background: #1A1520; border: 1px solid #3A2040; color: #7A5080;
    font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.2rem 0.6rem; border-radius: 20px; font-family: 'DM Mono', monospace;
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0B0E14; }
::-webkit-scrollbar-thumb { background: #2A3044; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3A4258; }
</style>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#7A84A0", size=12),
    margin=dict(l=16, r=16, t=24, b=16),
    xaxis=dict(gridcolor="#1E2332", linecolor="#1E2332", tickfont=dict(color="#5A6278")),
    yaxis=dict(gridcolor="#1E2332", linecolor="#1E2332", tickfont=dict(color="#5A6278")),
)

init_db()

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="sidebar-brand-icon">🕵️</span>
        <div>
            <div class="sidebar-brand-name">DarkLens</div>
            <div class="sidebar-brand-sub">Pattern Monitor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Manual Analysis", "Monitoring Management", "Historical Analytics"],
        label_visibility="collapsed"
    )
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:0 0.4rem'>
        <div style='font-size:0.7rem;color:#3A4258;text-transform:uppercase;
                    letter-spacing:0.12em;font-family:DM Mono,monospace'>
            v1.0.0 · Anthropic Powered
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — MANUAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
if page == "Manual Analysis":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Manual Analysis</h1>
        <p class="page-subtitle">Scan any URL for dark patterns and manipulative UX signals.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Target URL</div>', unsafe_allow_html=True)
    url = st.text_input("Website URL", placeholder="https://example.com", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚡  Run Analysis", use_container_width=True):
        if not url:
            st.warning("Please enter a valid URL before running analysis.")
            st.stop()
        with st.spinner("Running AI analysis — this may take a moment…"):
            results = analyze_website(url)
        st.session_state["last_results"] = results
        st.session_state["last_url"] = url

    if "last_results" in st.session_state:
        results = st.session_state["last_results"]
        url     = st.session_state["last_url"]
        score   = results["score"]
        risk    = results["risk_level"]

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        if risk == "LOW":
            st.markdown("""
            <div class="risk-low">
                <div class="risk-label">🟢 Low Manipulation Risk</div>
                <div class="risk-description">This site shows minimal signs of dark patterns.</div>
            </div>""", unsafe_allow_html=True)
        elif risk == "MODERATE":
            st.markdown("""
            <div class="risk-moderate">
                <div class="risk-label">🟡 Moderate Manipulation Risk</div>
                <div class="risk-description">Some concerning patterns were detected. Review snippets below.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="risk-high">
                <div class="risk-label">🔴 High Manipulation Risk</div>
                <div class="risk-description">Significant dark patterns detected. Proceed with caution.</div>
            </div>""", unsafe_allow_html=True)

        col_gauge, col_metrics = st.columns([3, 2], gap="large")

        with col_gauge:
            st.markdown('<div class="section-label">Manipulation Score</div>', unsafe_allow_html=True)
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={'font': {'family': 'Syne', 'size': 38, 'color': '#E8ECF5'}},
                title={'text': "", 'font': {'color': '#5A6278'}},
                gauge={
                    'axis': {
                        'range': [0, 1],
                        'tickcolor': '#2A3044',
                        'tickfont': {'color': '#5A6278', 'size': 10},
                    },
                    'bar': {'color': '#61AFEF', 'thickness': 0.22},
                    'bgcolor': '#1A2035',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 0.1],  'color': '#0D2818'},
                        {'range': [0.1, 0.25], 'color': '#261E0A'},
                        {'range': [0.25, 1],  'color': '#280D0D'},
                    ],
                    'threshold': {
                        'line': {'color': '#E74C3C', 'width': 2},
                        'thickness': 0.7,
                        'value': 0.25
                    }
                }
            ))
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=10),
                height=220,
                font=dict(family="DM Sans", color="#7A84A0")
            )
            st.plotly_chart(gauge, use_container_width=True)

        with col_metrics:
            st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:0.8rem">
                <div class="metric-value">{results['total_snippets']}</div>
                <div class="metric-label">Total Snippets Scanned</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#E74C3C">{results['dark_count']}</div>
                <div class="metric-label">Dark Pattern Snippets</div>
            </div>
            """, unsafe_allow_html=True)

        if results["category_breakdown"]:
            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Category Breakdown</div>', unsafe_allow_html=True)
            df_cat = pd.DataFrame(
                list(results["category_breakdown"].items()),
                columns=["Category", "Count"]
            )
            donut = px.pie(
                df_cat, names="Category", values="Count", hole=0.55,
                color_discrete_sequence=["#61AFEF","#E06C75","#98C379","#E5C07B","#C678DD","#56B6C2"]
            )
            donut.update_traces(
                textfont_size=12, textfont_color="#D6DCE8",
                marker=dict(line=dict(color="#0B0E14", width=2))
            )
            donut.update_layout(
                **CHART_LAYOUT, height=300,
                legend=dict(font=dict(color="#7A84A0", size=11),
                            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(donut, use_container_width=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Detailed Snippet Analysis</div>', unsafe_allow_html=True)

        for idx, snippet in enumerate(results["dark_snippets"]):
            with st.expander(f"{idx+1}. {snippet['label']}  ·  confidence {snippet['confidence']:.2f}"):
                st.markdown(f"""
                <div style="font-size:0.88rem;color:#C0C8DC;line-height:1.6;margin-bottom:0.9rem">
                    {snippet['text']}
                </div>
                <div>
                    {''.join(f'<span class="token-chip">{t}</span>' for t in snippet['tokens'])}
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        if st.button("💾  Store This Result"):
            save_analysis(
                url, results["score"], results["risk_level"],
                results["total_snippets"], results["dark_count"]
            )
            st.success("Result stored in the database.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MONITORING MANAGEMENT 
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Monitoring Management":

    # 🔹 TITLE ONLY (clean)
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Monitoring Management</h1>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # MANUAL TRIGGER
    # =========================
    if st.button("▶ Run Monitoring Now"):
        with st.spinner("Running monitoring..."):
            messages = run_monitoring_cycle()
        for msg in messages:
            st.write(msg)

    st.divider()

    # =========================
    # ADD NEW SITE (CLEAN INPUT)
    # =========================
    col1, col2 = st.columns([4,1])

    with col1:
        new_monitor_url = st.text_input(
            "Enter URL",
            placeholder="https://site.com",
            label_visibility="collapsed"
        )

    with col2:
        if st.button("Add"):
            if new_monitor_url:
                add_monitored_site(new_monitor_url)
                st.success("Added successfully")
                st.rerun()

    st.divider()

    # =========================
    # REGISTERED SITES + RUN COUNT
    # =========================
    sites = get_monitored_sites()
    history = get_all_analyses()

    if sites:

        df_hist = pd.DataFrame(history, columns=[
            "ID","URL","Score","Risk","Total Snippets","Dark Snippets","Timestamp"
        ])

        st.subheader("Registered Sites")

        for site in sites:
            site_id, site_url, is_active = site

            # 🔹 RUN COUNT
            if not df_hist.empty:
                run_count = len(df_hist[df_hist["URL"] == site_url])
            else:
                run_count = 0

            status = "🟢 Active" if is_active else "🟡 Paused"

            col1, col2, col3, col4 = st.columns([4,1,1,1])

            with col1:
                st.write(site_url)
                st.caption(f"Runs: {run_count}")

            with col2:
                if is_active:
                    if st.button("Pause", key=f"p_{site_id}"):
                        toggle_site_status(site_id, 0)
                        st.rerun()
                else:
                    if st.button("Resume", key=f"r_{site_id}"):
                        toggle_site_status(site_id, 1)
                        st.rerun()

            with col3:
                if st.button("Delete", key=f"d_{site_id}"):
                    delete_site_completely(site_id)
                    st.success("Deleted")
                    st.rerun()

            with col4:
                st.write(status)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — HISTORICAL ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Historical Analytics":

    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Historical Analytics</h1>
        <p class="page-subtitle">Website-wise Dark Pattern Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    history = get_all_analyses()

    if history:

        df_history = pd.DataFrame(history, columns=[
            "ID","URL","Score","Risk","Total Snippets","Dark Snippets","Timestamp"
        ])

        df_history["Timestamp"] = pd.to_datetime(df_history["Timestamp"])
        df_history = df_history.sort_values("Timestamp")

        # =========================
        #  FILTER BY WEBSITE
        # =========================
        selected_url = st.selectbox(
            "Select Website",
            ["All"] + list(df_history["URL"].unique())
        )

        if selected_url != "All":
            df_history = df_history[df_history["URL"] == selected_url]

        st.markdown("<hr>", unsafe_allow_html=True)

        # =========================
        #  SUMMARY METRICS
        # =========================
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Runs", len(df_history))
        col2.metric("Avg Score", f"{df_history['Score'].mean():.2f}")
        col3.metric("High Risk", len(df_history[df_history["Risk"]=="HIGH"]))
        col4.metric("Avg Dark Snippets", f"{df_history['Dark Snippets'].mean():.2f}")

        st.divider()

        # =========================
        # ✅ SCORE TREND
        # =========================
        st.subheader("Manipulation Score Trend")

        fig_time = px.line(
            df_history,
            x="Timestamp",
            y="Score",
            markers=True
        )

        st.plotly_chart(fig_time, use_container_width=True)

        st.divider()

        # =========================
        # ✅ DARK PATTERN DISTRIBUTION
        # =========================
        st.subheader("Dark Pattern Distribution")

        fig_box = px.box(
            df_history,
            y="Dark Snippets"
        )

        st.plotly_chart(fig_box, use_container_width=True)

        st.divider()

        # =========================
        #  RISK DISTRIBUTION
        # =========================
        st.subheader("Risk Distribution")

        fig_risk = px.pie(
            df_history,
            names="Risk"
        )

        st.plotly_chart(fig_risk, use_container_width=True)

        st.divider()

        # =========================
        #  WEBSITE RANKING
        # =========================
        if selected_url == "All":

            st.subheader("Most Manipulative Websites")

            ranking = df_history.groupby("URL")["Score"].mean().sort_values(ascending=False)

            fig_rank = px.bar(
                x=ranking.index,
                y=ranking.values,
                labels={"x":"Website","y":"Avg Score"}
            )

            st.plotly_chart(fig_rank, use_container_width=True)

    else:
        st.info("No historical data available yet.")