"""
pages/3_Analytics_Dashboard.py
Interactive Exploratory Data Analysis & Diagnostic Charts.
"""

import streamlit as st
from utils.header import render_header
from utils.charts import EDA_CHARTS_CATALOG, build_figure
from utils.model_cache import (
    prepare_dataset,
    get_primary_model_context,
    get_classifier_suite_context,
    get_cv_scores,
)

st.set_page_config(page_title="Analytics Dashboard", page_icon="📈", layout="wide")
render_header()

project_opt = st.session_state.project_option

st.title(f"📈 Exploratory Data Analysis: {project_opt} Track")
charts = EDA_CHARTS_CATALOG.get(project_opt, [])
st.markdown(f"Displaying **{len(charts)} mandatory visualizations** calibrated for viva presentation with non-causal observations.")

raw_df = st.session_state.get("_effective_active_df")
if raw_df is None:
    st.error(
        "🛑 No active dataset loaded. Use the **Upload Dataset** button in the top navigation bar "
        "to populate this dashboard."
    )
    st.stop()


try:
    active_df, cleaning_summary = prepare_dataset(raw_df, project_opt)
except Exception as e:
    st.error(f"Failed to prepare dataset for charting: {e}")
    st.stop()

with st.expander("🧹 Data Cleaning & Feature Engineering Applied to This Run", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows (raw → cleaned)", f"{cleaning_summary.get('initial_rows', 0):,} → {cleaning_summary.get('final_rows', 0):,}")
    c2.metric("Duplicates Removed", f"{cleaning_summary.get('duplicates_removed', 0):,}")
    c3.metric("Engineered Feature Columns", f"{active_df.shape[1] - raw_df.shape[1]:,}")
    st.caption(
        "Cleaning + feature engineering (utils.preprocessing.clean_dataframe + "
        "utils.feature_engineering.engineer_features) run automatically on whichever "
        "dataset is active — bundled or your own upload — before any chart or model below."
    )

needs_primary_model = any(
    chart["type"] in {"scatter_fit", "residual", "horizontal_bar", "confusion_matrix", "audit_bar"}
    for chart in charts
)
needs_classifier_suite = any(chart["type"] == "roc_curve" for chart in charts)
needs_cv = any(chart["id"] == "CHART_H11" for chart in charts)

primary_ctx = None
multi_ctx = None
cv_scores = None

with st.spinner("Training diagnostic models for this track..."):
    if needs_primary_model:
        try:
            primary_ctx = get_primary_model_context(active_df, project_opt)
        except Exception as e:
            st.warning(f"Model-dependent charts unavailable: {e}")
    if needs_classifier_suite:
        try:
            multi_ctx = get_classifier_suite_context(active_df, project_opt)
        except Exception as e:
            st.warning(f"ROC comparison unavailable: {e}")
    if needs_cv:
        try:
            cv_scores = get_cv_scores(active_df, project_opt)
        except Exception as e:
            st.warning(f"Cross-validation chart unavailable: {e}")

for chart in charts:
    with st.expander(f"{chart['id']}: {chart['title']}", expanded=True):
        st.caption(f"ℹ️ **Observation Caption**: {chart['caption']}")
        fig = build_figure(
            chart["id"], project_opt, active_df,
            primary_ctx=primary_ctx, multi_ctx=multi_ctx, cv_scores=cv_scores,
        )
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, key=f"plot_{chart['id']}")
        else:
            st.info("Chart could not be rendered for the current dataset — check back after the next deploy.")
