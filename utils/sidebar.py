"""
utils/sidebar.py
Shared Capstone Control Panel (Data Ingestion Mode + Project Track Switcher).

Rendered identically at the TOP of the sidebar on every page via
render_control_panel(), so the ingestion/upload controls are always visible
(not just on the home page) and the active dataset/source selection persists
across page navigation and reruns.
"""

from typing import Any, Optional

import streamlit as st

from utils.data_source import (
    BundledCSVSource,
    UploadedFileSource,
    WebhookPushSource,
    DatabaseReadOnlySource,
    RestAPIPullSource,
)

PROJECT_OPTIONS = ["SALES", "CHURN", "HR_ATTRITION"]

TRACK_LABELS = {
    "SALES": "1: Sales Analytics & Profit Prediction",
    "CHURN": "2: Customer Churn Prediction",
    "HR_ATTRITION": "3: HR Analytics & Employee Attrition",
}
TARGET_COLUMNS = {
    "SALES": "Profit",
    "CHURN": "Churned",
    "HR_ATTRITION": "Attrition",
}
BUNDLED_FILES = {
    "SALES": "data/sales_dataset.csv",
    "CHURN": "data/churn_dataset.csv",
    "HR_ATTRITION": "data/hr_attrition_dataset.csv",
}
SOURCE_OPTIONS = {
    "bundled": "1. Bundled CSV Archive (Default)",
    "upload": "2. User File Upload (Session-Only)",
    "webhook": "3. Webhook Drop Zone (HMAC Verified)",
    "database": "4. Database Read-Only (SQL SELECT)",
    "api": "5. External REST API Endpoint",
}


def _init_state() -> None:
    defaults = {
        "active_source_key": "bundled",
        "project_option": "SALES",
        "_prev_project_option": "SALES",
        "column_mapping": {},
        "active_data_hash": "",
        "active_df": None,
        "active_meta": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_data(show_spinner=False)
def _load_bundled(file_path: str):
    return BundledCSVSource(file_path=file_path).load()


def render_control_panel() -> None:
    """Renders the ingestion + track control panel at the top of the current
    page's sidebar, and keeps st.session_state.active_df / active_meta in
    sync with whatever source is currently selected. Call this once near the
    top of every page script, right after st.set_page_config()."""
    _init_state()

    st.sidebar.title("🎛️ Capstone Control Panel")
    st.sidebar.caption("Student: **Jawed Iqbal** | DS & ML Capstone")

    # --- Data Ingestion Mode (moved to the top, persists via key=) ---
    st.sidebar.subheader("📥 Data Ingestion Mode")
    st.sidebar.radio(
        "Active Ingestion Adapter:",
        list(SOURCE_OPTIONS.keys()),
        format_func=lambda k: SOURCE_OPTIONS[k],
        key="active_source_key",
    )
    selected_source = st.session_state.active_source_key

    current_adapter: Optional[Any] = None
    active_df = None
    meta_obj = None

    if selected_source == "bundled":
        file_path = BUNDLED_FILES[st.session_state.project_option]
        current_adapter = BundledCSVSource(file_path=file_path)
        st.sidebar.info(f"Using {current_adapter.describe()}")
        try:
            active_df, meta_obj = _load_bundled(file_path)
        except Exception as e:
            st.sidebar.error(f"Error loading bundled data: {e}")

    elif selected_source == "upload":
        uploaded = st.sidebar.file_uploader(
            "Upload CSV or Excel dataset:", type=["csv", "xlsx", "xls"], key="uploader_widget"
        )
        if uploaded is not None:
            current_adapter = UploadedFileSource(uploaded_file=uploaded, filename=uploaded.name)
            try:
                active_df, meta_obj = current_adapter.load()
                st.sidebar.success(f"✅ Loaded `{uploaded.name}` ({active_df.shape[0]:,} rows)")
            except Exception as e:
                st.sidebar.error(f"Failed to parse uploaded file: {e}")
        elif st.session_state.get("active_df") is not None and st.session_state.get("_last_upload_name"):
            # No new file re-selected on this page/rerun — keep using the last
            # upload for the rest of the session instead of dropping it.
            active_df = st.session_state.active_df
            meta_obj = st.session_state.active_meta
            st.sidebar.success(f"Using previously uploaded `{st.session_state['_last_upload_name']}` for this session.")
        else:
            st.sidebar.warning("Awaiting file upload...")

        if current_adapter and active_df is not None:
            st.session_state["_last_upload_name"] = uploaded.name

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

    if current_adapter:
        st.sidebar.caption(f"**Currently using**: {current_adapter.describe()}")
    if meta_obj:
        st.sidebar.markdown(f"**Loaded At**: `{meta_obj.loaded_at[:19]}Z`")
        st.sidebar.markdown(f"**Rows**: `{meta_obj.row_count}` | **Columns**: `{meta_obj.column_count}`")
        st.sidebar.caption(f"SHA256: `{meta_obj.sha256[:16]}...`")

    if active_df is not None:
        st.session_state.active_df = active_df
        st.session_state.active_meta = meta_obj
    else:
        # Nothing this branch produced (e.g. "upload" selected but no file
        # chosen yet, and none uploaded earlier this session) — don't let a
        # stale dataset from a previously selected mode linger silently.
        st.session_state.active_df = None
        st.session_state.active_meta = None

    if st.sidebar.button("🔄 Reload Bundled Data"):
        st.cache_data.clear()
        st.session_state.active_source_key = "bundled"
        st.session_state.pop("_last_upload_name", None)
        st.rerun()

    st.sidebar.markdown("---")

    # --- Project Track Switcher ---
    selected_track = st.sidebar.selectbox(
        "Select Project Track:",
        PROJECT_OPTIONS,
        index=PROJECT_OPTIONS.index(st.session_state.project_option),
    )
    if selected_track != st.session_state.project_option:
        st.session_state.project_option = selected_track
        st.session_state.column_mapping = {}
        if st.session_state.active_source_key == "bundled":
            st.session_state.active_df = None
        st.rerun()

    st.sidebar.markdown(f"**Track**: {TRACK_LABELS[st.session_state.project_option]}")
    st.sidebar.markdown(f"**Target Column**: `{TARGET_COLUMNS[st.session_state.project_option]}`")

    st.sidebar.markdown("---")
    st.sidebar.warning(
        "⚠️ **Streamlit Cloud Deployment Reality**: "
        "Streamlit Community Cloud has an ephemeral filesystem. Uploaded files and webhook-received files "
        "do not survive a restart. The bundled demo dataset is always available. For persistent storage, "
        "connect external Supabase/S3 (documented in README)."
    )
