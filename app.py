"""
app.py
Streamlit Application Entry Point.

Data Science & Machine Learning Capstone
Student: Jawed Iqbal | Course: Data Science and Machine Learning
Multi-Source Data Ingestion Architecture & Predictive Analytics Platform
"""

import streamlit as st

# Configure page layout and aesthetics
st.set_page_config(
    page_title="DS & ML Capstone — Multi-Source Ingestion",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.header import render_header, TRACK_PILL_LABELS as TRACK_LABELS, TARGET_COLUMNS
from utils.validation import validate_dataset

# Renders the shared ingestion/upload + track-switcher control panel at the
# top of the sidebar, and syncs st.session_state.active_df / active_meta.
render_header()

active_df = st.session_state.get("_effective_active_df")
meta_obj = st.session_state.get("_effective_active_meta")

# MAIN APP BODY
st.title("Data Science & Machine Learning Capstone Platform")
st.markdown(f"### {TRACK_LABELS[st.session_state.project_option]}")

# Ethical banner if HR_ATTRITION per §5
if st.session_state.project_option == "HR_ATTRITION":
    st.warning(
        "🛡️ **MANDATORY ETHICAL WORKFORCE GOVERNANCE BANNER**: "
        "This prediction is intended for workforce-level analysis and voluntary retention support. "
        "It must not be used as the sole basis for termination, promotion, salary, disciplinary, or hiring decisions."
    )

# Cold start / Missing dataset check per §1 & §4
if active_df is None:
    st.error(
        "🛑 **MISSING_DATASET STATE**: "
        "No active dataset is currently loaded. Please ensure `data/dataset.csv` exists or upload a dataset "
        "using the **Upload Dataset** button in the top navigation bar. Analysis and modeling are locked until data arrives."
    )
    st.stop()

# Schema Validation Gate per §2.6
st.subheader("🔍 Schema Validation Gate")
target_col = TARGET_COLUMNS[st.session_state.project_option]

if st.session_state.project_option == "SALES":
    required_cols = ["Sales", "Quantity", "Discount", "Shipping_Cost", "Region", "Category", "Sub_Category"]
elif st.session_state.project_option == "CHURN":
    required_cols = ["Tenure_Months", "Contract_Type", "Monthly_Charges", "Total_Charges", "Support_Tickets", "Complaints"]
else:
    required_cols = ["Age", "Department", "Job_Role", "Monthly_Income", "Job_Level", "Years_At_Company", "Overtime", "Work_Life_Balance"]

report = validate_dataset(
    df=active_df,
    required_columns=required_cols,
    target_column=target_col,
    column_mapping=st.session_state.column_mapping
)

if report.is_valid:
    st.success(f"✅ Schema Validation Passed: All {report.total_columns_required} required columns and target '{target_col}' verified.")
else:
    st.error(f"❌ Schema Validation Failed: Status `{report.schema_status}`. Missing columns detected.")
    for msg in report.summary_messages:
        st.write(f"- {msg}")

    # Column Mapping UI per §2.6
    st.markdown("#### 🧩 Column-Mapping Interface")
    st.caption("Map existing dataset columns to canonical model features below:")
    existing_cols = list(active_df.columns) if hasattr(active_df, "columns") else []

    cols_grid = st.columns(min(3, max(1, len(report.missing_columns))))
    for idx, missing_col in enumerate(report.missing_columns):
        col_ui = cols_grid[idx % len(cols_grid)]
        suggested = report.suggested_mappings.get(missing_col, "")
        opts = ["-- Select mapping --"] + existing_cols
        def_idx = opts.index(suggested) if suggested in opts else 0
        mapped_choice = col_ui.selectbox(f"Map `{missing_col}` to:", opts, index=def_idx, key=f"map_{missing_col}")
        if mapped_choice != "-- Select mapping --":
            st.session_state.column_mapping[missing_col] = mapped_choice

    if st.button("Apply Column Mappings"):
        st.rerun()

# Overview metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ingestion Adapter", meta_obj.source_type if meta_obj else "Unknown")
m2.metric("Total Rows", f"{len(active_df):,}" if hasattr(active_df, "__len__") else "0")
m3.metric("Total Columns", f"{len(active_df.columns)}" if hasattr(active_df, "columns") else "0")
m4.metric("ML Training Gate", "Ready ✅" if report.can_train_ml else "Locked 🔒")

st.markdown("---")
st.markdown("### 📑 Explore Capstone Pages in Left Navigation")
st.info("Use the Streamlit multipage sidebar navigation on the left to explore Data Explorer, Dashboards, Preprocessing Labs, Model Evaluation, and Real-Time Inference.")
