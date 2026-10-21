"""
pages/6_Business_Recommendations.py
Executive Business Recommendations with Numbered Evidence Citations.
"""

import streamlit as st
from utils.recommendations import RECOMMENDATIONS

st.set_page_config(page_title="Business Recommendations", page_icon="💡", layout="wide")

from utils.sidebar import render_control_panel
render_control_panel()
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"💡 Actionable Business Recommendations: {project_opt}")
st.markdown("Every recommendation adheres to strict **Finding -> Evidence -> Recommendation -> Expected Outcome** standards.")

recs = RECOMMENDATIONS.get(project_opt, [])
st.markdown(f"Total Strategic Recommendations: **{len(recs)} items**")

for rec in recs:
    with st.container():
        st.markdown(f"### 📌 {rec['id']}: {rec['finding']}")
        st.markdown(f"**🔍 Evidence**: *{rec['evidence']}*")
        st.info(f"**⚡ Recommended Action**: {rec['recommendation']}")
        st.success(f"**📈 Expected Business Outcome**: {rec['expected_outcome']}")
        st.markdown("---")
