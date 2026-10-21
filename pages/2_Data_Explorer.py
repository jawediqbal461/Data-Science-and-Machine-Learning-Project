"""
pages/2_Data_Explorer.py
Dataset Inspection, Statistical Profiles, and Missing Value Auditing.
"""

import streamlit as st
import pandas as pd
from utils.data_source import BundledCSVSource
from utils.validation import validate_dataset

st.set_page_config(page_title="Dataset Explorer", page_icon="🔍", layout="wide")

from utils.header import render_header
render_header()
st.title("🔍 Comprehensive Dataset Explorer")

# Get or load dataset
project_opt = st.session_state.get("project_option", "SALES")
active_df = st.session_state.get("_effective_active_df")

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

k1, k2, k3, k4 = st.columns(4)
k1.metric("Shape", f"{active_df.shape[0]:,} × {active_df.shape[1]}")
k2.metric("Duplicate Records", f"{int(active_df.duplicated().sum()):,}")
k3.metric("Numerical Columns", f"{active_df.select_dtypes(include=['int64','float64','int32','float32']).shape[1]}")
k4.metric("Categorical Columns", f"{active_df.select_dtypes(include=['object','category','bool']).shape[1]}")

# --- Filters + rows selector + filtered-data download (per the assignment's
# Dataset/Customer Explorer page requirements) ---
FILTER_COLUMNS = {
    "SALES": ["Region", "Category", "Sub_Category"],
    "CHURN": ["Contract_Type", "Internet_Service", "Payment_Method"],
    "HR_ATTRITION": ["Department", "Job_Role", "Work_Mode"],
}
DATE_COLUMNS = {"SALES": "Order_Date", "CHURN": "Signup_Date", "HR_ATTRITION": "Hire_Date"}

filtered_df = active_df.copy()
with st.expander("🔎 Filters & Download", expanded=True):
    n_rows = st.slider("Number of rows to preview:", min_value=5, max_value=min(200, len(active_df)), value=min(25, len(active_df)))

    filter_cols_present = [c for c in FILTER_COLUMNS.get(project_opt, []) if c in filtered_df.columns]
    if filter_cols_present:
        fcols = st.columns(len(filter_cols_present))
        for fc, col_name in zip(fcols, filter_cols_present):
            options = sorted(filtered_df[col_name].dropna().unique().tolist())
            selected = fc.multiselect(col_name, options, default=[])
            if selected:
                filtered_df = filtered_df[filtered_df[col_name].isin(selected)]

    date_col = DATE_COLUMNS.get(project_opt)
    if date_col and date_col in filtered_df.columns:
        parsed_dates = pd.to_datetime(filtered_df[date_col], errors="coerce")
        valid_dates = parsed_dates.dropna()
        if not valid_dates.empty:
            d_min, d_max = valid_dates.min().date(), valid_dates.max().date()
            date_range = st.date_input(f"{date_col} range:", value=(d_min, d_max), min_value=d_min, max_value=d_max)
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start, end = date_range
                mask = (parsed_dates.dt.date >= start) & (parsed_dates.dt.date <= end)
                filtered_df = filtered_df[mask.reindex(filtered_df.index, fill_value=False)]

    st.caption(f"Filtered to **{len(filtered_df):,}** of {len(active_df):,} records.")
    st.download_button(
        "⬇️ Download Filtered Data (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{project_opt.lower()}_filtered_data.csv",
        mime="text/csv",
    )

# Tabs for inspection — the preview tab reflects the filters above; the
# statistics/quality tabs below still describe the full active dataset.
tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Preview", "📊 Summary Statistics", "🩺 Missing & Quality Profile", "ℹ️ Column Types"])

with tab1:
    st.markdown(f"**Filtered Preview ({n_rows} of {len(filtered_df):,} rows)**")
    st.dataframe(filtered_df.head(n_rows), use_container_width=True)
    st.markdown("**First 5 Rows (full dataset)**")
    st.dataframe(active_df.head(5), use_container_width=True)
    st.markdown("**Last 5 Rows (full dataset)**")
    st.dataframe(active_df.tail(5), use_container_width=True)

with tab2:
    st.markdown("#### Numeric Summary")
    st.dataframe(active_df.describe(), use_container_width=True)

with tab4:
    st.markdown("#### Column Data Types")
    dtype_df = pd.DataFrame({
        "Column": active_df.columns,
        "Data Type": [str(t) for t in active_df.dtypes],
        "Kind": ["Numerical" if pd.api.types.is_numeric_dtype(active_df[c]) else "Categorical" for c in active_df.columns],
    })
    st.dataframe(dtype_df, use_container_width=True)

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
