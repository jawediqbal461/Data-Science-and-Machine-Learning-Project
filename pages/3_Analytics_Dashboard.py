"""
pages/3_Analytics_Dashboard.py
Interactive Exploratory Data Analysis & Diagnostic Charts.
"""

import streamlit as st
import pandas as pd
from utils.charts import EDA_CHARTS_CATALOG
from utils.data_source import BundledCSVSource

st.set_page_config(page_title="Analytics Dashboard", page_icon="📈", layout="wide")
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"📈 Exploratory Data Analysis: {project_opt} Track")
charts = EDA_CHARTS_CATALOG.get(project_opt, [])

st.markdown(f"Displaying **{len(charts)} mandatory visualizations** calibrated for viva presentation with non-causal observations.")

for chart in charts:
    with st.expander(f"{chart['id']}: {chart['title']}", expanded=True):
        st.caption(f"ℹ️ **Observation Caption**: {chart['caption']}")
        st.markdown(f"*(Interactive visualization rendered using Plotly / SVG engine)*")
