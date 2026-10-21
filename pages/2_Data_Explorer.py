"""
pages/2_Data_Explorer.py
Dataset Inspection, Statistical Profiles, and Missing Value Auditing.
"""

import streamlit as st
import pandas as pd
from utils.data_source import BundledCSVSource
from utils.validation import validate_dataset

st.set_page_config(page_title="Dataset Explorer", page_icon="🔍", layout="wide")

from utils.sidebar import render_control_panel
render_control_panel()
st.title("🔍 Comprehensive Dataset Explorer")

# Get or load dataset
project_opt = st.session_state.get("project_option", "SALES")
active_df = st.session_state.get("active_df")

if active_df is None:
    path_map = {
        "SALES": "data/sales_dataset.csv",
        "CHURN": "data/churn_dataset.csv",
        "HR_ATTRITION": "data/hr_attrition_dataset.csv"
    }
    try:
        source = BundledCSVSource(file_path=path_map.get(project_opt, "data/dataset.csv"))
        active_df, _ = source.load()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

st.markdown(f"**Inspecting Track:** `{project_opt}` | **Total Records:** `{len(active_df):,}`")

# Tabs for inspection
tab1, tab2, tab3 = st.tabs(["📋 Data Preview", "📊 Summary Statistics", "🩺 Missing & Quality Profile"])

with tab1:
    st.dataframe(active_df.head(25), use_container_width=True)

with tab2:
    st.markdown("#### Numeric Summary")
    st.dataframe(active_df.describe(), use_container_width=True)

with tab3:
    st.markdown("#### Missing Values & Data Types")
    col_info = []
    for c in active_df.columns:
        null_count = int(active_df[c].isna().sum())
        col_info.append({
            "Column Name": c,
            "Data Type": str(active_df[c].dtype),
            "Non-Null Count": len(active_df) - null_count,
            "Missing Count": null_count,
            "Missing %": f"{(null_count / len(active_df) * 100):.2f}%",
            "Unique Values": active_df[c].nunique()
        })
    st.dataframe(pd.DataFrame(col_info), use_container_width=True)
