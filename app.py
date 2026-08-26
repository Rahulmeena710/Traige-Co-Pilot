# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Local module imports
from engine import TriageEngine
from simulation import generate_patient_records, apply_surge_condition


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Triage Co-Pilot | Accenture Innovation Challenge 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. CUSTOM UI / CSS
# ============================================================

st.markdown(
    """<style>
    /* Global Page Styling */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    /* Hero Header */
    .hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 55%, #0E7490 100%);
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 22px;
        color: #FFFFFF;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 850;
        letter-spacing: -0.03em;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        color: #CBD5E1;
        font-size: 0.98rem;
        margin-bottom: 15px;
    }

    .hero-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 6px 11px;
        border-radius: 999px;
        font-size: 0.76rem;
        margin-right: 7px;
    }

    /* Section Labels */
    .section-label {
        color: #64748B;
        font-size: 0.73rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 12px 0 8px 2px;
    }

    /* KPI Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
    }

    .metric-card-danger { border-top: 4px solid #EF4444; }
    .metric-card-warning { border-top: 4px solid #F59E0B; }
    .metric-card-success { border-top: 4px solid #10B981; }

    .metric-title {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #64748B;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }

    /* Priority Badges */
    .badge-p1 {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .badge-p2 {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .badge-p3 {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
    }

    /* Deterioration Alert Ticker */
    .ticker-container {
        background-color: #FFF1F2;
        border: 1px solid #FECDD3;
        border-left: 5px solid #E11D48;
        padding: 13px 18px;
        border-radius: 9px;
        color: #881337;
        font-size: 0.9rem;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(225, 29, 72, 0.05);
    }

    /* Streamlit Component Overrides */
    .queue-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 4px;
        box-shadow: 0 3px 12px rgba(15,23,42,0.035);
        margin-bottom: 10px;
    }

    .stExpander {
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        background: #FFFFFF;
        overflow: hidden;
    }

    .mini-stat {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: center;
    }

    .mini-stat-label {
        font-size: 0.68rem;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
    }

    .mini-stat-value {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 2px;
    }

    .status-online {
        color: #047857;
        font-weight: 750;
    }

    [data-testid="stSidebar"] {
        background: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }

    .stButton > button {
        border-radius: 999px;
        font-weight: 700;
    }

    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 0.75rem;
        padding: 22px 0 4px;
    }
</style>""",
    unsafe_allow_html=True,
)


# ============================================================
# 3. LOAD AI ENGINE
# ============================================================

@st.cache_resource
def load_engine():
    return TriageEngine()


engine = load_engine()


# ============================================================
# 4. SESSION STATE MANAGEMENT
# ============================================================

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "patients" not in st.session_state:
    st.session_state.patients = generate_patient_records()


# ============================================================
# 5. SIDEBAR CONTROL PANEL
# ============================================================

with st.sidebar:
    st.markdown("### 🎛️ Clinical Control Center")
    st.caption("Accenture Innovation Challenge 2026")
    st.markdown("---")

    surge_active = st.toggle("⚡ Trigger 3× Surge Load", value=False)

    if st.button("🔄 Refresh Patient Queue", use_container_width=True):
        st.session_state.patients = generate_patient_records()
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🔍 Queue Search & Filter")

    search_query = st.text_input(
        "Search ID or Symptom:",
        placeholder="e.g. chest pain, P-102",
    )

    selected_levels = st.multiselect(
        "Priority Filter:",
        options=["P1 - Critical", "P2 - Urgent", "P3 - Non-Urgent"],
        default=["P1 - Critical", "P2 - Urgent", "P3 - Non-Urgent"],
    )

    st.markdown("---")
    st.caption("AI-assisted clinical decision support system.")


# ============================================================
# 6. HERO HEADER
# ============================================================

st.markdown(
    """<div class="hero">
    <div class="hero-title">🏥 Triage Co-Pilot</div>
    <div class="hero-subtitle">
        Real-time AI-assisted patient prioritization and queue deterioration analytics
    </div>
    <span class="hero-pill">● AI Engine Online</span>
    <span class="hero-pill">Live Queue Monitoring</span>
    <span class="hero-pill">Clinician-in-the-loop</span>
</div>""",
    unsafe_allow_html=True,
)


# ============================================================
# 7. DATA INFERENCE PIPELINE
# ============================================================

current_patients = (
    apply_surge_condition(st.session_state.patients, multiplier=3)
    if surge_active
    else st.session_state.patients
)

processed_data = []

for p in current_patients:
    symptoms = engine.extract_nlp_symptoms(p.get("clinical_notes", ""))
    p_data = {**p, "symptoms": symptoms}

    score, uncertainty, category = engine.evaluate_patient(p_data)

    processed_data.append(
        {
            **p_data,
            "risk_score": score,
            "uncertainty": uncertainty,
            "triage_category": category,
            "extracted_symptoms": ", ".join(symptoms) if symptoms else "None",
        }
    )


# ============================================================
# 8. CREATE DATAFRAME & SORT
# ============================================================

df = pd.DataFrame(processed_data)

if not df.empty:
    df = df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)
else:
    df = pd.DataFrame(
        columns=[
            "patient_id",
            "age",
            "hr",
            "sbp",
            "spo2",
            "temp",
            "clinical_notes",
            "risk_score",
            "uncertainty",
            "triage_category",
            "extracted_symptoms",
        ]
    )


# ============================================================
# 9. FILTER DATA
# ============================================================

filtered_df = df[df["triage_category"].isin(selected_levels)]

if search_query:
    sq = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["patient_id"].astype(str).str.lower().str.contains(sq, na=False)
        | filtered_df["clinical_notes"].astype(str).str.lower().str.contains(sq, na=False)
        | filtered_df["extracted_symptoms"].astype(str).str.lower().str.contains(sq, na=False)
    ]


# ============================================================
# 10. KPI DASHBOARD
# ============================================================

st.markdown('<div class="section-label">Operational Snapshot</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

p1_count = len(df[df["triage_category"] == "P1 - Critical"]) if not df.empty else 0
p2_count = len(df[df["triage_category"] == "P2 - Urgent"]) if not df.empty else 0
p3_count = len(df[df["triage_category"] == "P3 - Non-Urgent"]) if not df.empty else 0

with kpi1:
    st.markdown(
        f"""<div class="metric-card">
            <div class="metric-title">Active Queue</div>
            <div class="metric-value">{len(df)}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""<div class="metric-card metric-card-danger">
            <div class="metric-title">P1 - Critical</div>
            <div class="metric-value" style="color:#EF4444;">{p1_count}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""<div class="metric-card metric-card-warning">
            <div class="metric-title">P2 - Urgent</div>
            <div class="metric-value" style="color:#F59E0B;">{p2_count}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""<div class="metric-card metric-card-success">
            <div class="metric-title">P3 - Non-Urgent</div>
            <div class="metric-value" style="color:#10B981;">{p3_count}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with kpi5:
    status_text = "3× Surge" if surge_active else "1× Normal"
    status_color = "#EF4444" if surge_active else "#10B981"
    st.markdown(
        f"""<div class="metric-card">
            <div class="metric-title">Surge State</div>
            <div class="metric-value" style="color:{status_color};">{status_text}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# 11. REAL-TIME DETERIORATION ALERT
# ============================================================

if not df.empty:
    critical_cases = df[(df["spo2"] < 90) | (df["risk_score"] > 80)]

    if not critical_cases.empty:
        top_critical = critical_cases.iloc[0]
        st.markdown(
            f"""<div class="ticker-container">
            🚨 <b>REAL-TIME DETERIORATION ALERT:</b> Patient <b>{top_critical["patient_id"]}</b> is at critical risk 
            (Risk Score: <b>{top_critical["risk_score"]}</b> | SpO2: <b>{top_critical["spo2"]}%</b> | HR: <b>{top_critical["hr"]} bpm</b>). 
            Immediate clinical evaluation required.
        </div>""",
            unsafe_allow_html=True,
        )


# ============================================================
# 12. LIVE OPERATIONS STATUS
# ============================================================

st.markdown('<div class="section-label">Live Clinical Operations</div>', unsafe_allow_html=True)

mode_text = "SURGE" if surge_active else "NORMAL"

st.markdown(
    f"""<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px;">
        <div class="mini-stat" style="min-width:145px;">
            <div class="mini-stat-label">System</div>
            <div class="mini-stat-value"><span class="status-online">● Online</span></div>
        </div>
        <div class="mini-stat" style="min-width:145px;">
            <div class="mini-stat-label">Cases Visible</div>
            <div class="mini-stat-value">{len(filtered_df)}</div>
        </div>
        <div class="mini-stat" style="min-width:145px;">
            <div class="mini-stat-label">Critical</div>
            <div class="mini-stat-value" style="color:#DC2626;">{p1_count}</div>
        </div>
        <div class="mini-stat" style="min-width:145px;">
            <div class="mini-stat-label">Mode</div>
            <div class="mini-stat-value">{mode_text}</div>
        </div>
    </div>""",
    unsafe_allow_html=True,
)


# ============================================================
# 13. MAIN SPLIT SCREEN
# ============================================================

left_col, right_col = st.columns([1.25, 1])


# ------------------------------------------------------------
# LEFT COLUMN: LIVE TRIAGE QUEUE
# ------------------------------------------------------------
with left_col:
    st.subheader(f"📋 Live Triage Queue ({len(filtered_df)} matches)")

    if filtered_df.empty:
        st.info("No patient cases match your current filter criteria.")
    else:
        for idx, row in filtered_df.iterrows():

            if "P1" in str(row["triage_category"]):
                badge_html = f'<span class="badge-p1">{row["triage_category"]}</span>'
            elif "P2" in str(row["triage_category"]):
                badge_html = f'<span class="badge-p2">{row["triage_category"]}</span>'
            else:
                badge_html = f'<span class="badge-p3">{row["triage_category"]}</span>'

            header_text = (
                f"#{idx + 1} | {row['patient_id']} (Age {row['age']}) — Risk: {row['risk_score']}"
            )

            st.markdown('<div class="queue-card">', unsafe_allow_html=True)

            with st.expander(header_text):
                st.markdown(
                    f"**Current Classification:** {badge_html}",
                    unsafe_allow_html=True,
                )
                st.write("")

                # Patient details split
                v_col, c_col = st.columns(2)

                with v_col:
                    st.markdown("**Vitals & Metrics**")
                    st.write(f"• **Heart Rate:** `{row['hr']} bpm`")
                    st.write(f"• **Blood Pressure:** `{row['sbp']} mmHg`")
                    st.write(f"• **SpO2:** `{row['spo2']}%`")
                    st.write(f"• **Temperature:** `{row['temp']} °C`")
                    st.write(f"• **AI Uncertainty:** `{row['uncertainty']}`")

                with c_col:
                    st.markdown("**Clinical Notes & Symptoms**")
                    st.write(f"*{row['clinical_notes']}*")
                    st.write(f"**NLP Detected:** `{row['extracted_symptoms']}`")

                st.markdown("---")

                # Clinician override interface
                with st.form(key=f"override_{row['patient_id']}"):
                    o_col1, o_col2 = st.columns([2, 1])

                    with o_col1:
                        reason = st.text_input(
                            "Override Reason:",
                            key=f"r_{row['patient_id']}",
                        )

                    with o_col2:
                        new_cat = st.selectbox(
                            "Reassign:",
                            ["P1 - Critical", "P2 - Urgent", "P3 - Non-Urgent"],
                            key=f"cat_{row['patient_id']}",
                        )

                    submitted = st.form_submit_button("Confirm Override", use_container_width=True)

                    if submitted:
                        st.session_state.audit_log.append(
                            {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "patient_id": row["patient_id"],
                                "from": row["triage_category"],
                                "to": new_cat,
                                "reason": reason if reason else "Clinician Override",
                            }
                        )
                        st.success(f"Overridden {row['patient_id']} → {new_cat}")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# RIGHT COLUMN: VISUAL INTELLIGENCE & ANALYTICS
# ------------------------------------------------------------
with right_col:
    st.subheader("💡 Visual Intelligence & Analytics")

    if not df.empty:
        # Chart 1: Risk vs Age
        fig_scatter = px.scatter(
            df,
            x="age",
            y="risk_score",
            color="triage_category",
            size="uncertainty",
            hover_data=["patient_id", "clinical_notes"],
            title="<b>Patient Risk vs. Demographics</b>",
            color_discrete_map={
                "P1 - Critical": "#EF4444",
                "P2 - Urgent": "#F59E0B",
                "P3 - Non-Urgent": "#10B981",
            },
            template="plotly_white",
            height=380,
        )

        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#F8FAFC",
            margin=dict(l=20, r=20, t=50, b=20),
            legend_title_text="Priority",
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        # Chart 2: Priority Distribution
        fig_donut = px.pie(
            df,
            names="triage_category",
            title="<b>Queue Severity Mix</b>",
            color="triage_category",
            color_discrete_map={
                "P1 - Critical": "#EF4444",
                "P2 - Urgent": "#F59E0B",
                "P3 - Non-Urgent": "#10B981",
            },
            hole=0.5,
            template="plotly_white",
            height=320,
        )

        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=50, b=20),
            legend_title_text="Priority",
        )

        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No data available to plot visual intelligence charts.")


# ============================================================
# 14. AUDIT LOG SECTION
# ============================================================

st.markdown("---")

with st.expander("📜 Clinician Override Audit Logs"):
    if st.session_state.audit_log:
        audit_df = pd.DataFrame(st.session_state.audit_log)
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No overrides recorded in the current session.")


# ============================================================
# 15. FOOTER
# ============================================================

st.markdown(
    """<div class="footer">
    Triage Co-Pilot • AI-assisted decision support • Accenture Innovation Challenge 2026
</div>""",
    unsafe_allow_html=True,
)