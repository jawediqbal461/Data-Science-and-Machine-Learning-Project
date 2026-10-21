"""
utils/header.py
Sticky top navigation header for the Capstone Platform, mirroring the
AI-Studio React UI (DS logo, pill track-selector, Test Mode toggle,
Upload Dataset modal, Download Zip, and a Target Column / Benchmark /
Active Source info strip).

Call render_header() once near the top of every page, right after
st.set_page_config(). It owns st.session_state.active_df / active_meta /
active_source_key / project_option, same as utils.sidebar did before.
"""

import io
import os
import zipfile
from datetime import datetime, timezone
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

TRACK_PILL_LABELS = {
    "SALES": "1. Sales & Profit",
    "CHURN": "2. Customer Churn",
    "HR_ATTRITION": "3. HR Attrition",
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
BENCHMARK_INFO = {
    "SALES": {"model": "Random Forest Regressor", "score": "R² = 0.884 | MAE = $14.20"},
    "CHURN": {"model": "Gradient Boosting Classifier", "score": "F1 = 0.858 | ROC-AUC = 0.931"},
    "HR_ATTRITION": {"model": "Random Forest Classifier", "score": "F1 = 0.853 | 5-Fold CV = 0.849"},
}
SOURCE_LABELS = {
    "bundled": "Bundled CSV Archive",
    "upload": "User File Upload",
    "webhook": "Webhook Drop Zone",
    "database": "Database Read-Only",
    "api": "External REST API",
}

_HEADER_CSS = """
<style>
section[data-testid="stSidebarNav"] { padding-top: 0.5rem; }
div.capstone-header {
    position: sticky; top: 0; z-index: 999;
    background: rgba(15, 23, 42, 0.97);
    border-bottom: 1px solid #1E293B;
    padding: 0.85rem 1.1rem 0.6rem 1.1rem;
    margin: -1rem -1rem 1.1rem -1rem;
    backdrop-filter: blur(6px);
}
div.capstone-header .cp-title-row { display:flex; align-items:center; gap:0.7rem; }
div.capstone-header .cp-logo {
    width:38px; height:38px; border-radius:10px; flex-shrink:0;
    background: linear-gradient(135deg,#2563EB,#4F46E5 55%,#38BDF8);
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-weight:800; font-size:0.95rem;
    box-shadow:0 4px 14px rgba(37,99,235,0.35);
}
div.capstone-header .cp-title { font-weight:700; color:#F1F5F9; font-size:1.02rem; line-height:1.15; }
div.capstone-header .cp-meta { color:#94A3B8; font-size:0.72rem; margin-top:2px; }
div.capstone-header .cp-meta b { color:#CBD5E1; }
div.capstone-header .cp-meta .deadline { color:#60A5FA; font-weight:600; }
div.capstone-header .cp-strip {
    margin-top:0.65rem; padding-top:0.5rem; border-top:1px solid rgba(148,163,184,0.15);
    display:flex; flex-wrap:wrap; justify-content:space-between; gap:0.5rem;
    font-size:0.72rem; color:#94A3B8;
}
div.capstone-header .cp-badge {
    font-family: ui-monospace, Menlo, monospace; font-size:0.72rem;
    padding:1px 7px; border-radius:5px; border:1px solid #1E3A8A;
    background:rgba(30,58,138,0.35); color:#93C5FD;
}
div.capstone-header .cp-badge.src { border-color:#334155; background:rgba(30,41,59,0.8); color:#38BDF8; }
div.capstone-header .cp-bench { color:#34D399; font-family: ui-monospace, Menlo, monospace; }

div[data-testid="stSegmentedControl"] label p { font-size:0.78rem !important; font-weight:600; }
</style>
"""


def _init_state() -> None:
    defaults = {
        "active_source_key": "bundled",
        "project_option": "SALES",
        "column_mapping": {},
        "active_df": None,
        "active_meta": None,
        "simulate_missing_dataset": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_data(show_spinner=False)
def _load_bundled(file_path: str):
    return BundledCSVSource(file_path=file_path).load()


def _build_submission_zip() -> bytes:
    """Zips the Python/config submission files (skips data caches, node
    artifacts, and anything hidden) for the Download Zip button."""
    root = os.getcwd()
    skip_dirs = {".git", "__pycache__", "node_modules", "dist", ".aistudio", "data/incoming"}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith(".")]
            for fname in filenames:
                if fname.endswith((".pyc", ".zip")):
                    continue
                rel_path = os.path.normpath(os.path.join(rel_dir, fname))
                if rel_path.split(os.sep)[0] in skip_dirs:
                    continue
                zf.write(os.path.join(dirpath, fname), arcname=rel_path)
    buf.seek(0)
    return buf.getvalue()


def _render_source_status() -> None:
    """Small inline status line used inside the upload dialog."""
    meta = st.session_state.active_meta
    if meta:
        st.caption(
            f"Loaded `{meta.source_type}` — {meta.row_count} rows × {meta.column_count} cols "
            f"at {meta.loaded_at[:19]}Z"
        )


@st.dialog("📤 Upload / Connect a Dataset")
def _upload_dialog() -> None:
    track = st.session_state.project_option
    st.caption(f"Loading data for track: **{TRACK_PILL_LABELS[track]}**")

    tab_upload, tab_webhook, tab_db, tab_api, tab_bundled = st.tabs(
        ["📁 File Upload", "🔗 Webhook", "🗄️ Database", "🌐 REST API", "📦 Bundled"]
    )

    with tab_upload:
        uploaded = st.file_uploader("Upload CSV or Excel dataset:", type=["csv", "xlsx", "xls"], key="dialog_uploader")
        if uploaded is not None:
            try:
                source = UploadedFileSource(uploaded_file=uploaded, filename=uploaded.name)
                df, meta = source.load()
                st.session_state.active_df = df
                st.session_state.active_meta = meta
                st.session_state.active_source_key = "upload"
                st.session_state["_last_upload_name"] = uploaded.name
                st.success(f"✅ Loaded `{uploaded.name}` ({df.shape[0]:,} rows × {df.shape[1]} cols)")
                if st.button("Use this dataset", type="primary", key="use_upload_btn"):
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to parse file: {e}")

    with tab_webhook:
        source = WebhookPushSource(incoming_dir="data/incoming")
        st.caption(source.describe())
        if st.button("Check webhook drop zone", key="check_webhook_btn"):
            try:
                df, meta = source.load()
                st.session_state.active_df = df
                st.session_state.active_meta = meta
                st.session_state.active_source_key = "webhook"
                st.success(f"✅ Loaded {df.shape[0]:,} rows from webhook drop zone")
                st.rerun()
            except Exception as e:
                st.warning(f"No webhook file yet: {e}")

    with tab_db:
        source = DatabaseReadOnlySource(table_name="capstone_records")
        st.caption(source.describe())
        st.code("SELECT * FROM capstone_records WHERE is_active=true", language="sql")
        st.info("Read-only SQL adapter — configure a connection URI in `st.secrets` to activate.")

    with tab_api:
        source = RestAPIPullSource(endpoint_url="https://api.analytics-pipeline.org/v1/stream")
        st.caption(source.describe())
        st.info("Authenticated REST pull — configure an API key in `st.secrets` to activate.")

    with tab_bundled:
        file_path = BUNDLED_FILES[track]
        st.caption(f"Reset back to the bundled demo archive: `{file_path}`")
        if st.button("Use bundled dataset", key="use_bundled_btn"):
            st.cache_data.clear()
            st.session_state.active_source_key = "bundled"
            st.session_state.pop("_last_upload_name", None)
            st.rerun()


def render_header() -> None:
    """Renders the sticky top navbar + info strip, and keeps
    st.session_state.active_df / active_meta in sync with the active
    source. Call once near the top of every page."""
    _init_state()
    st.markdown(_HEADER_CSS, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="capstone-header">', unsafe_allow_html=True)

        col_title, col_tabs, col_actions = st.columns([2.4, 4.4, 3.2], vertical_alignment="center")

        with col_title:
            st.markdown(
                f"""
                <div class="cp-title-row">
                    <div class="cp-logo">DS</div>
                    <div>
                        <div class="cp-title">Data Science & ML Capstone Platform</div>
                        <div class="cp-meta"><b>Student: Jawed Iqbal</b> · Course: Data Science &amp; ML ·
                        <span class="deadline">Deadline: 22 Oct 2026</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_tabs:
            try:
                selected = st.segmented_control(
                    "Project Track",
                    options=PROJECT_OPTIONS,
                    format_func=lambda k: TRACK_PILL_LABELS[k],
                    key="project_option",
                    label_visibility="collapsed",
                )
            except Exception:
                selected = st.radio(
                    "Project Track",
                    options=PROJECT_OPTIONS,
                    format_func=lambda k: TRACK_PILL_LABELS[k],
                    key="project_option",
                    horizontal=True,
                    label_visibility="collapsed",
                )
            if selected and selected != st.session_state.get("_prev_project_option", selected):
                st.session_state.column_mapping = {}
                if st.session_state.active_source_key == "bundled":
                    st.session_state.active_df = None
            st.session_state["_prev_project_option"] = selected

        with col_actions:
            a1, a2, a3 = st.columns([0.9, 1.9, 1.2])
            with a1:
                test_mode = st.toggle(
                    "🧪 Test",
                    value=st.session_state.simulate_missing_dataset,
                    help="Developer tool: simulate what happens when no dataset is loaded.",
                    key="simulate_missing_dataset",
                )
            with a2:
                if st.button("⬆️ Upload", use_container_width=True, type="primary",
                             help="Upload a dataset or connect another ingestion adapter"):
                    _upload_dialog()
            with a3:
                st.download_button(
                    "⬇️ Zip",
                    data=_build_submission_zip(),
                    file_name=f"Jawed_Iqbal_DataScience_Capstone_{st.session_state.project_option}_Submission.zip",
                    mime="application/zip",
                    use_container_width=True,
                    help="Download the project source as a submission .zip",
                )

        st.markdown("</div>", unsafe_allow_html=True)

    # --- resolve the active dataset for this rerun ---
    selected_source = st.session_state.active_source_key
    active_df = None
    meta_obj = None

    if selected_source == "bundled":
        file_path = BUNDLED_FILES[st.session_state.project_option]
        try:
            active_df, meta_obj = _load_bundled(file_path)
        except Exception as e:
            st.error(f"Error loading bundled data: {e}")
    elif st.session_state.active_df is not None:
        # upload / webhook / database / api — whatever the dialog last loaded
        active_df = st.session_state.active_df
        meta_obj = st.session_state.active_meta

    if active_df is not None:
        st.session_state.active_df = active_df
        st.session_state.active_meta = meta_obj
    elif selected_source == "bundled":
        st.session_state.active_df = None
        st.session_state.active_meta = None

    if st.session_state.simulate_missing_dataset:
        # Developer "Test Mode" override — keep the real data cached but
        # present the rest of the app with nothing loaded.
        effective_df = None
        effective_meta = None
    else:
        effective_df = st.session_state.active_df
        effective_meta = st.session_state.active_meta

    # --- info strip ---
    track = st.session_state.project_option
    bench = BENCHMARK_INFO[track]
    meta = effective_meta
    source_badge = (
        f"{meta.source_type} ({meta.row_count} rows, {meta.column_count} cols)"
        if meta else "No active source"
    )
    st.markdown(
        f"""
        <div class="capstone-header" style="margin-top:-1rem; padding-top:0; border-top:none;">
            <div class="cp-strip">
                <div>
                    <span>Target Column:</span>
                    <span class="cp-badge">{TARGET_COLUMNS[track]}</span>
                    &nbsp;|&nbsp;
                    <span>Benchmark Pipeline:</span> <b style="color:#E2E8F0;">{bench['model']}</b>
                    <span class="cp-bench">({bench['score']})</span>
                </div>
                <div>
                    <span>Active Source:</span>
                    <span class="cp-badge src">{source_badge}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Expose the effective (Test-Mode-aware) dataset for the page to use.
    st.session_state["_effective_active_df"] = effective_df
    st.session_state["_effective_active_meta"] = effective_meta
