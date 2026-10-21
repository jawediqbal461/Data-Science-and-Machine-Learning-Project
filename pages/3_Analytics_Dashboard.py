"""
pages/3_Analytics_Dashboard.py
Interactive Exploratory Data Analysis & Diagnostic Charts.
"""

import streamlit as st
from utils.charts import (
    EDA_CHARTS_CATALOG,
    build_figure,
    train_primary_model,
    train_classifier_suite,
    run_cross_validation,
)
from utils.data_source import BundledCSVSource
from utils.preprocessing import clean_dataframe

st.set_page_config(page_title="Analytics Dashboard", page_icon="📈", layout="wide")
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"📈 Exploratory Data Analysis: {project_opt} Track")
charts = EDA_CHARTS_CATALOG.get(project_opt, [])
st.markdown(f"Displaying **{len(charts)} mandatory visualizations** calibrated for viva presentation with non-causal observations.")

PATH_MAP = {
    "SALES": "data/sales_dataset.csv",
    "CHURN": "data/churn_dataset.csv",
    "HR_ATTRITION": "data/hr_attrition_dataset.csv",
}


@st.cache_data(show_spinner=False)
def _load_clean_data(project_option: str):
    source = BundledCSVSource(file_path=PATH_MAP.get(project_option, "data/dataset.csv"))
    raw_df, _ = source.load()
    cleaned_df, _ = clean_dataframe(raw_df, project_option=project_option)
    return cleaned_df


@st.cache_resource(show_spinner=False)
def _get_primary_model_context(project_option: str, row_count: int):
    df = _load_clean_data(project_option)
    return train_primary_model(df, project_option)


@st.cache_resource(show_spinner=False)
def _get_classifier_suite_context(project_option: str, row_count: int):
    df = _load_clean_data(project_option)
    return train_classifier_suite(df, project_option)


@st.cache_resource(show_spinner=False)
def _get_cv_scores(project_option: str, row_count: int):
    df = _load_clean_data(project_option)
    return run_cross_validation(df, project_option)


try:
    active_df = _load_clean_data(project_opt)
except Exception as e:
    st.error(f"Failed to load dataset for charting: {e}")
    st.stop()

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
            primary_ctx = _get_primary_model_context(project_opt, len(active_df))
        except Exception as e:
            st.warning(f"Model-dependent charts unavailable: {e}")
    if needs_classifier_suite:
        try:
            multi_ctx = _get_classifier_suite_context(project_opt, len(active_df))
        except Exception as e:
            st.warning(f"ROC comparison unavailable: {e}")
    if needs_cv:
        try:
            cv_scores = _get_cv_scores(project_opt, len(active_df))
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
