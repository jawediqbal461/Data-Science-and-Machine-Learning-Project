"""
pages/6_Business_Recommendations.py
Executive Business Recommendations with Numbered Evidence Citations.

Every "Evidence" line and "Expected Outcome" figure is computed LIVE from
whichever dataset (bundled or uploaded) is currently active — see
utils/recommendations.py. Nothing on this page is a fixed placeholder.
"""

import streamlit as st

from utils.header import render_header
from utils.model_cache import prepare_dataset, get_primary_model_context
from utils.recommendations import build_recommendations

st.set_page_config(page_title="Business Recommendations", page_icon="💡", layout="wide")
render_header()
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"💡 Actionable Business Recommendations: {project_opt}")
st.markdown("Every recommendation follows **Finding → Evidence → Recommendation → Expected Outcome** — Evidence and Expected Outcome are computed live from the active dataset below, never fixed text.")

raw_df = st.session_state.get("_effective_active_df")
if raw_df is None:
    st.error(
        "🛑 No active dataset loaded. Use the **Upload Dataset** button in the top "
        "navigation bar to populate this page."
    )
    st.stop()

with st.spinner("Computing live evidence from the active dataset..."):
    try:
        active_df, _ = prepare_dataset(raw_df, project_opt)
    except Exception as e:
        st.error(f"Failed to prepare dataset: {e}")
        st.stop()

    model_ctx = None
    if project_opt in ("CHURN", "HR_ATTRITION"):
        try:
            model_ctx = get_primary_model_context(active_df, project_opt)
        except Exception:
            model_ctx = None

    recs = build_recommendations(active_df, project_opt, model_ctx)

if not recs:
    st.info(
        "The active dataset doesn't have the columns needed to compute any live recommendations "
        "for this track. Try switching to a bundled dataset or uploading a file with the expected schema."
    )
    st.stop()

k1, k2, k3 = st.columns(3)
k1.metric("Strategic Recommendations", f"{len(recs)}")
k2.metric("Records Analyzed", f"{len(active_df):,}")
k3.metric("Evidence Source", "Live — active dataset")

st.markdown("---")

for i, rec in enumerate(recs, start=1):
    with st.container(border=True):
        st.markdown(f"#### 📌 {i}. {rec['finding']}")
        st.caption(rec["id"])
        st.markdown(f"**🔍 Evidence**  \n{rec['evidence']}")
        st.info(f"**⚡ Recommended Action**  \n{rec['recommendation']}")
        st.success(f"**📈 Expected Business Outcome**  \n{rec['expected_outcome']}")
