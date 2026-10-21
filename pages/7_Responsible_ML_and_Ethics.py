"""
pages/7_Responsible_ML_and_Ethics.py
Responsible Machine Learning, Subgroup Fairness Auditing, and Workforce Ethics.

Computes the subgroup equity audit LIVE from the trained model's held-out
test predictions on whichever dataset is actually active, instead of a
fixed demo table — and only for the classification tracks (Churn, HR
Attrition) where "Actual/Predicted rate, Recall, FPR" is a meaningful
audit; Sales is a regression problem and gets a short explanatory note.
"""

import pandas as pd
import streamlit as st
from sklearn.metrics import recall_score, confusion_matrix

from utils.header import render_header
from utils.model_cache import prepare_dataset, get_primary_model_context

st.set_page_config(page_title="Responsible ML & Ethics", page_icon="⚖️", layout="wide")
render_header()
project_opt = st.session_state.get("project_option", "SALES")

st.title("⚖️ Responsible ML & Subgroup Fairness Review")

if project_opt == "HR_ATTRITION":
    st.warning(
        "🛡️ **MANDATORY ETHICAL WORKFORCE GOVERNANCE BANNER**: "
        "This prediction is intended for workforce-level analysis and voluntary retention support. "
        "It must not be used as the sole basis for termination, promotion, salary, disciplinary, or hiring decisions."
    )

# Which categorical columns to audit by, per track — chosen from columns
# that actually exist in each bundled/uploaded schema.
GROUP_CANDIDATES = {
    "HR_ATTRITION": ["Gender", "Department", "Work_Mode"],
    "CHURN": ["Gender", "Contract_Type", "Internet_Service"],
}

if project_opt not in GROUP_CANDIDATES:
    st.info(
        "📎 Subgroup fairness auditing (group size, actual vs. predicted rate, recall, false-positive "
        "rate) applies to the two **classification** tracks — **Customer Churn** and **HR Attrition**. "
        "Sales & Profit is a regression problem, so this specific audit format doesn't apply; see the "
        "Model Evaluation page for its residual and error-distribution diagnostics instead."
    )
    st.stop()

raw_df = st.session_state.get("_effective_active_df")
if raw_df is None:
    st.error(
        "🛑 No active dataset loaded. Use the **Upload Dataset** button in the top navigation bar "
        "to populate this page."
    )
    st.stop()

try:
    active_df, _ = prepare_dataset(raw_df, project_opt)
except Exception as e:
    st.error(f"Failed to prepare dataset: {e}")
    st.stop()

with st.spinner("Scoring held-out test records for subgroup audit..."):
    try:
        ctx = get_primary_model_context(active_df, project_opt)
    except Exception as e:
        st.error(f"Could not train the audit model on the active dataset: {e}")
        st.stop()

group_cols = [c for c in GROUP_CANDIDATES[project_opt] if c in active_df.columns]
if not group_cols:
    st.warning("None of the expected demographic/segment columns were found in the active dataset to audit by.")
    st.stop()

y_test = ctx["y_test"]
preds = ctx["preds"]
test_idx = y_test.index

st.markdown("### 📋 Subgroup Equity Audit — computed live on the held-out test split")
st.caption(
    f"Evaluates the production pipeline's parity across {', '.join(group_cols)} slices "
    f"({len(test_idx):,} held-out test records). Flags small subgroups (n < 30)."
)


def _audit_rows(group_col: str) -> list:
    labels = active_df.loc[test_idx, group_col].astype(str)
    rows = []
    for group_val in sorted(labels.dropna().unique()):
        mask = (labels == group_val).values
        n = int(mask.sum())
        if n == 0:
            continue
        y_g = y_test[mask]
        p_g = preds[mask]
        actual_rate = float(y_g.mean()) if n > 0 else 0.0
        predicted_rate = float((p_g == 1).mean()) if n > 0 else 0.0
        try:
            recall = recall_score(y_g, p_g, zero_division=0)
        except Exception:
            recall = 0.0
        try:
            cm = confusion_matrix(y_g, p_g, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        except Exception:
            fpr = 0.0
        rows.append({
            "Subgroup Category": f"{group_col}: {group_val}",
            "Sample Size (n)": n,
            "Actual Rate": f"{actual_rate * 100:.1f}%",
            "Predicted Rate": f"{predicted_rate * 100:.1f}%",
            "Recall": f"{recall * 100:.1f}%",
            "FPR": f"{fpr * 100:.1f}%",
            "Disparity Alert": "⚠️ Small Sample (n < 30)" if n < 30 else "Nominal",
        })
    return rows


audit_data = []
for gc in group_cols:
    audit_data.extend(_audit_rows(gc))

if audit_data:
    audit_df = pd.DataFrame(audit_data)
    st.dataframe(audit_df, use_container_width=True)

    nominal_recalls = [
        float(r["Recall"].rstrip("%")) for r in audit_data if r["Disparity Alert"] == "Nominal"
    ]
    if len(nominal_recalls) >= 2:
        spread = max(nominal_recalls) - min(nominal_recalls)
        st.info(
            f"🔍 **Audit Conclusion**: Recall spread across adequately-sized subgroups (n ≥ 30) is "
            f"**{spread:.1f} percentage points** on this run's held-out test split. "
            + ("This is within a typical tolerance band." if spread < 10 else
               "This exceeds a 10-point band — worth reviewing feature inputs for proxy bias before relying on this model for any individual-level decision.")
        )
    st.caption(
        "Subgroups with n < 30 should rely on qualitative oversight rather than this model's "
        "quantitative metrics, since small-sample recall/FPR estimates are unstable."
    )
else:
    st.info("No subgroup rows could be computed for the active dataset's test split.")
