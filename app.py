"""
app.py
Streamlit Application Entry Point.

Data Science & Machine Learning Capstone
Student: Jawed Iqbal | Course: Data Science and Machine Learning
Multi-Source Data Ingestion Architecture & Predictive Analytics Platform
"""

import os
import streamlit as st

# Configure page layout and aesthetics
st.set_page_config(
    page_title="DS & ML Capstone — Multi-Source Ingestion",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.data_source import (
    BundledCSVSource,
    UploadedFileSource,
    WebhookPushSource,
    DatabaseReadOnlySource,
    RestAPIPullSource,
    DataSourceMeta
)
from utils.validation import validate_dataset, ValidationReport
from utils.preprocessing import clean_dataframe, EXCLUSION_RULES
from utils.recommendations import RECOMMENDATIONS

# Session state initialization per §2.4
if "active_source_key" not in st.session_state:
    st.session_state.active_source_key = "bundled"

if "project_option" not in st.session_state:
    st.session_state.project_option = "SALES"

if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {}

if "active_data_hash" not in st.session_state:
    st.session_state.active_data_hash = ""

if "active_df" not in st.session_state:
    st.session_state.active_df = None


# Caching logic per §2.4 & §7
@st.cache_data
def load_bundled_data(file_path: str, project_option: str):
    source = BundledCSVSource(file_path=file_path)
    return source.load()


# SIDEBAR: Project Option & Data Source Selector
st.sidebar.title("🎛️ Capstone Control Panel")
st.sidebar.caption("Student: **Jawed Iqbal** | DS & ML Capstone")

# Project Track Switcher
project_options = ["SALES", "CHURN", "HR_ATTRITION"]
selected_track = st.sidebar.selectbox(
    "Select Project Track:",
    project_options,
    index=project_options.index(st.session_state.project_option)
)
if selected_track != st.session_state.project_option:
    st.session_state.project_option = selected_track
    st.session_state.column_mapping = {}
    st.session_state.active_df = None
    st.rerun()

track_labels = {
    "SALES": "1: Sales Analytics & Profit Prediction",
    "CHURN": "2: Customer Churn Prediction",
    "HR_ATTRITION": "3: HR Analytics & Employee Attrition"
}
target_columns = {
    "SALES": "Profit",
    "CHURN": "Churned",
    "HR_ATTRITION": "Attrition"
}
bundled_files = {
    "SALES": "data/sales_dataset.csv",
    "CHURN": "data/churn_dataset.csv",
    "HR_ATTRITION": "data/hr_attrition_dataset.csv"
}

st.sidebar.markdown(f"**Track**: {track_labels[st.session_state.project_option]}")
st.sidebar.markdown(f"**Target Column**: `{target_columns[st.session_state.project_option]}`")
st.sidebar.markdown("---")

# Data Source Selection (§2)
st.sidebar.subheader("📥 Data Ingestion Mode")
source_options = {
    "bundled": "1. Bundled CSV Archive (Default)",
    "upload": "2. User File Upload (Session-Only)",
    "webhook": "3. Webhook Drop Zone (HMAC Verified)",
    "database": "4. Database Read-Only (SQL SELECT)",
    "api": "5. External REST API Endpoint"
}

selected_source = st.sidebar.radio(
    "Active Ingestion Adapter:",
    list(source_options.keys()),
    format_func=lambda k: source_options[k]
)
st.session_state.active_source_key = selected_source

# Render source-specific parameters in sidebar
current_adapter = None
active_df = None
meta_obj = None

if selected_source == "bundled":
    current_adapter = BundledCSVSource(file_path=bundled_files[st.session_state.project_option])
    st.sidebar.info(f"Using {current_adapter.describe()}")
    try:
        active_df, meta_obj = current_adapter.load()
    except Exception as e:
        st.sidebar.error(f"Error loading bundled data: {e}")

elif selected_source == "upload":
    uploaded = st.sidebar.file_uploader("Upload CSV or Excel dataset:", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        current_adapter = UploadedFileSource(uploaded_file=uploaded, filename=uploaded.name)
        active_df, meta_obj = current_adapter.load()
        st.session_state.active_df = active_df
    else:
        st.sidebar.warning("Awaiting file upload...")

elif selected_source == "webhook":
    current_adapter = WebhookPushSource(incoming_dir="data/incoming")
    st.sidebar.info(current_adapter.describe())
    try:
        active_df, meta_obj = current_adapter.load()
    except Exception as e:
        st.sidebar.warning(f"No webhook file yet: {e}")

elif selected_source == "database":
    current_adapter = DatabaseReadOnlySource(table_name="capstone_records")
    st.sidebar.info(current_adapter.describe())
    st.sidebar.code("SELECT * FROM capstone_records WHERE is_active=true", language="sql")

elif selected_source == "api":
    current_adapter = RestAPIPullSource(endpoint_url="https://api.analytics-pipeline.org/v1/stream")
    st.sidebar.info(current_adapter.describe())

# Sidebar Status Display per §2.1
if current_adapter:
    st.sidebar.caption(f"**Currently using**: {current_adapter.describe()}")
if meta_obj:
    st.sidebar.markdown(f"**Loaded At**: `{meta_obj.loaded_at[:19]}Z`")
    st.sidebar.markdown(f"**Rows**: `{meta_obj.row_count}` | **Columns**: `{meta_obj.column_count}`")
    st.sidebar.caption(f"SHA256: `{meta_obj.sha256[:16]}...`")

if st.sidebar.button("🔄 Reload Bundled Data"):
    st.cache_data.clear()
    st.session_state.active_source_key = "bundled"
    st.rerun()

# Streamlit Cloud Ephemeral Notice per §2.5
st.sidebar.markdown("---")
st.sidebar.warning(
    "⚠️ **Streamlit Cloud Deployment Reality**: "
    "Streamlit Community Cloud has an ephemeral filesystem. Uploaded files and webhook-received files "
    "do not survive a restart. The bundled demo dataset is always available. For persistent storage, "
    "connect external Supabase/S3 (documented in README)."
)

# MAIN APP BODY
st.title("Data Science & Machine Learning Capstone Platform")
st.markdown(f"### {track_labels[st.session_state.project_option]}")

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
        "using the `UploadedFileSource` in the left sidebar. Analysis and modeling are locked until data arrives."
    )
    st.stop()

# Schema Validation Gate per §2.6
st.subheader("🔍 Schema Validation Gate")
target_col = target_columns[st.session_state.project_option]

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
