"""
pages/1_Home.py
Executive Home & Project Overview.
"""

import streamlit as st

st.set_page_config(page_title="Executive Overview — Capstone", page_icon="🏠", layout="wide")

st.title("🏛️ Data Science & ML Capstone: Executive Overview")
st.markdown("### Capstone Assignment Project by **Jawed Iqbal**")
st.caption("Course: Data Science and Machine Learning | Submission Deadline: 22 October 2026")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="background-color: #1E293B; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB;">
        <h4 style="color:#60A5FA; margin-top:0;">Track 1: Sales Analytics</h4>
        <p style="font-size: 0.9em; color:#CBD5E1;">Profit regression forecasting, promotional discount elasticity, logistics cost-to-serve analysis, and loss avoidance warning engine.</p>
        <b>Target:</b> <code>Profit (USD)</code>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #1E293B; padding: 20px; border-radius: 10px; border-left: 5px solid #10B981;">
        <h4 style="color:#34D399; margin-top:0;">Track 2: Customer Churn</h4>
        <p style="font-size: 0.9em; color:#CBD5E1;">Subscriber retention optimization, friction scoring, dynamic threshold tuning slider, and revenue-at-risk calculations.</p>
        <b>Target:</b> <code>Churned (0/1)</code>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background-color: #1E293B; padding: 20px; border-radius: 10px; border-left: 5px solid #F59E0B;">
        <h4 style="color:#FBBF24; margin-top:0;">Track 3: HR Attrition</h4>
        <p style="font-size: 0.9em; color:#CBD5E1;">Workforce retention, 4-strategy imputation lab, subgroup equity audits, and strict ethical governance barriers.</p>
        <b>Target:</b> <code>Attrition (0/1)</code>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🏗️ Architectural Ingestion Pipeline")
st.info("""
This application implements an enterprise-grade **Adapter Pattern** decoupling data consumption from the storage medium:
1. **Bundled CSV Source (`BundledCSVSource`)**: Local disk archive serving as the resilient cold-start default.
2. **User Upload Source (`UploadedFileSource`)**: Isolated in-memory streaming via `st.file_uploader` (zero disk write for multi-tenant safety).
3. **Webhook Push Source (`WebhookPushSource`)**: Real-time streaming drop zone fed by a FastAPI sidecar authenticated via `HMAC-SHA256(body, WEBHOOK_SECRET)`.
4. **Database Read-Only Source (`DatabaseReadOnlySource`)**: Postgres/Supabase SQL connection restricted to non-destructive `SELECT` queries.
5. **REST API Pull Source (`RestAPIPullSource`)**: Polling external secure HTTPS endpoints.
""")

st.markdown("### 🛡️ Schema Gate & Ethical Directives")
st.markdown("""
- **Zero-Tolerance Leakage Rule**: Identifiers (`Order_ID`, `Customer_ID`, `Employee_ID`) and post-event columns (`Customer_Rating`, `Returned`, `Total_Sale`) are strictly isolated from feature inputs.
- **Fairness & Governance Policy**: All HR retention modeling contains prominent ethical warnings stating it must never be used for disciplinary, firing, or promotion discrimination.
""")
