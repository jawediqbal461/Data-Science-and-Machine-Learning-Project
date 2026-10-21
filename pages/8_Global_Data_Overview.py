"""
pages/8_Global_Data_Overview.py
Global Data Overview & Cross-Source Aggregated Statistics.

Computes real stats for every bundled dataset live from disk (not fixed
numbers), and for the dataset that's actually active right now — bundled
or your own upload — so the KPIs always match what's loaded.
"""

import streamlit as st
import pandas as pd

from utils.header import render_header, BUNDLED_FILES, TARGET_COLUMNS, TRACK_PILL_LABELS

st.set_page_config(page_title="Global Data Overview", page_icon="🌐", layout="wide")
render_header()

st.title("🌐 Global Data Overview: Cross-Source Aggregator")
st.markdown("Live statistics computed from the actual files on disk and whichever dataset is active right now — nothing below is a fixed placeholder.")


@st.cache_data(show_spinner=False)
def _profile_bundled(path: str, target: str) -> dict:
    df = pd.read_csv(path)
    target_series = pd.to_numeric(df[target], errors="coerce") if target in df.columns else None
    if target_series is not None and target_series.dropna().nunique() <= 2:
        pos = int((target_series == 1).sum())
        total = int(target_series.notna().sum())
        dist = f"{(total - pos) / total * 100:.1f}% Class 0 | {pos / total * 100:.1f}% Class 1 ({pos}/{total})"
    elif target_series is not None:
        dist = f"Mean: {target_series.mean():,.2f} | Min: {target_series.min():,.2f} | Max: {target_series.max():,.2f}"
    else:
        dist = "N/A"
    return {
        "rows": len(df),
        "cols": df.shape[1],
        "duplicates": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "target_distribution": dist,
    }


sources_summary = []
total_records = 0
total_features = 0
for track, path in BUNDLED_FILES.items():
    try:
        prof = _profile_bundled(path, TARGET_COLUMNS[track])
    except Exception as e:
        st.warning(f"Could not profile {path}: {e}")
        continue
    total_records += prof["rows"]
    total_features += prof["cols"]
    sources_summary.append({
        "Data Source": TRACK_PILL_LABELS[track],
        "Adapter Type": "BundledCSVSource",
        "File / URI": path,
        "Records": prof["rows"],
        "Features": prof["cols"],
        "Duplicate Rows": prof["duplicates"],
        "Missing Cells": prof["missing_cells"],
        "Target Column": TARGET_COLUMNS[track],
        "Target Distribution": prof["target_distribution"],
    })

active_df = st.session_state.get("_effective_active_df")
active_source_key = st.session_state.get("active_source_key", "bundled")
active_project = st.session_state.get("project_option", "SALES")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bundled Dataset Records", f"{total_records:,}", "Across 3 Tracks")
c2.metric("Bundled Feature Columns", f"{total_features:,}", "Raw Schema (pre-engineering)")
c3.metric("Currently Active Rows", f"{len(active_df):,}" if active_df is not None else "0", f"Source: {active_source_key}")
c4.metric("Active Track", active_project, TRACK_PILL_LABELS.get(active_project, ""))

st.markdown("---")
st.subheader("📊 Bundled Dataset Comparison Grid")
st.dataframe(pd.DataFrame(sources_summary), use_container_width=True)

st.caption(
    "The platform also supports Webhook, Database, and REST API ingestion adapters "
    "(see Home for the architecture) — those are illustrated there as alternative data "
    "paths for the same pipeline, not live external connections in this demo."
)

st.markdown("---")
st.subheader("🎯 Target Class Balance — Live From Disk")
col1, col2, col3 = st.columns(3)

for col, track in zip((col1, col2, col3), ["SALES", "CHURN", "HR_ATTRITION"]):
    try:
        prof = _profile_bundled(BUNDLED_FILES[track], TARGET_COLUMNS[track])
    except Exception:
        continue
    with col:
        st.markdown(f"**{TRACK_PILL_LABELS[track]}**")
        df_t = pd.read_csv(BUNDLED_FILES[track])
        target_series = pd.to_numeric(df_t[TARGET_COLUMNS[track]], errors="coerce")
        if target_series.dropna().nunique() <= 2:
            pos_rate = float((target_series == 1).mean())
            st.progress(min(max(1.0 - pos_rate, 0.0), 1.0))
        else:
            st.progress(min(max(float((target_series > 0).mean()), 0.0), 1.0))
        st.caption(prof["target_distribution"])

if active_df is not None:
    st.markdown("---")
    st.subheader(f"🔎 Currently Active Dataset Snapshot ({active_source_key})")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Rows", f"{len(active_df):,}")
    a2.metric("Columns", f"{active_df.shape[1]:,}")
    a3.metric("Duplicate Rows", f"{int(active_df.duplicated().sum()):,}")
    a4.metric("Missing Cells", f"{int(active_df.isna().sum().sum()):,}")
