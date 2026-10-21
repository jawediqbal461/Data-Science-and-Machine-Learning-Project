"""
utils/model_cache.py
Single shared cache layer so the Analytics Dashboard, Model Evaluation,
and Predictive Inference pages all train against the EXACT SAME cleaned +
feature-engineered dataset and the exact same fitted pipelines for a given
(dataset, track) pair, instead of three independent/divergent trainings.

This is what actually wires Task 2 (Data Cleaning), Task 3 (Feature
Engineering), Task 5/6 (Train multiple models + compare), and the
requirement that "the final model must be used inside the Streamlit
application" into the live app, rather than leaving the UI display
hardcoded benchmark numbers that ignore whatever dataset is active.
"""

from typing import Any, Dict, List, Tuple

import streamlit as st

from utils.preprocessing import clean_dataframe
from utils.feature_engineering import engineer_features
from utils.charts import train_primary_model, train_classifier_suite, run_cross_validation
from utils.modeling import train_and_evaluate


@st.cache_data(show_spinner=False)
def prepare_dataset(df: Any, project_option: str) -> Tuple[Any, Dict[str, Any]]:
    """Task 2 (cleaning) + Task 3 (feature engineering), applied identically
    everywhere the active dataset is consumed."""
    cleaned_df, cleaning_summary = clean_dataframe(df, project_option=project_option)
    engineered_df = engineer_features(cleaned_df, project_option=project_option)
    return engineered_df, cleaning_summary


@st.cache_resource(show_spinner=False)
def get_primary_model_context(df: Any, project_option: str) -> Dict[str, Any]:
    """Single production estimator per track — used for actual-vs-predicted,
    residuals, feature importance, and confusion-matrix charts."""
    return train_primary_model(df, project_option)


@st.cache_resource(show_spinner=False)
def get_classifier_suite_context(df: Any, project_option: str) -> Dict[str, Any]:
    """Multi-classifier suite (for ROC-curve comparison charts)."""
    return train_classifier_suite(df, project_option)


@st.cache_resource(show_spinner=False)
def get_cv_scores(df: Any, project_option: str) -> List[float]:
    return run_cross_validation(df, project_option)


@st.cache_resource(show_spinner=False)
def get_model_comparison(df: Any, project_option: str) -> Dict[str, Any]:
    """Task 5 (train >=3/4 models) + Task 6 (compare) + best-model selection,
    trained on whichever dataset is actually active (bundled or uploaded).
    Returns the real metrics table plus the fitted best_pipeline object that
    Predictive Inference uses for live scoring."""
    return train_and_evaluate(df, project_option=project_option)
