"""
pages/5_Predictive_Inference.py
Real-Time Inference Engine with Input Validation and Risk Band Scoring.

Scores every prediction with the ACTUAL best-performing pipeline selected
on pages/4_Model_Evaluation.py for the currently active dataset (not a
hand-written heuristic formula). Fields not exposed in the simplified
form are backfilled with the active dataset's median/mode so the row the
model sees is a realistic full-feature record.
"""

import pandas as pd
import streamlit as st

from utils.header import render_header
from utils.model_cache import prepare_dataset, get_model_comparison
from utils.prediction import classify_profit, classify_churn_risk

st.set_page_config(page_title="Predictive Inference Engine", page_icon="🔮", layout="wide")
render_header()
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"🔮 Real-Time Predictive Inference: {project_opt}")

raw_df = st.session_state.get("_effective_active_df")
if raw_df is None:
    st.error(
        "🛑 No active dataset loaded. Use the **Upload Dataset** button in the top "
        "navigation bar to populate this page."
    )
    st.stop()

try:
    active_df, _ = prepare_dataset(raw_df, project_opt)
except Exception as e:
    st.error(f"Failed to prepare dataset: {e}")
    st.stop()

with st.spinner("Loading the trained production pipeline for this dataset..."):
    try:
        comparison = get_model_comparison(active_df, project_opt)
    except Exception as e:
        st.error(f"The production pipeline could not be trained on the active dataset: {e}")
        st.stop()

feature_cols = comparison["metadata"]["features"]
best_name = comparison["metadata"]["best_model"]


def _baseline_row() -> dict:
    """Median (numeric) / mode (categorical) of every modeled feature, so the
    single-row DataFrame sent to the pipeline always has a realistic value
    for fields the simplified form below doesn't ask the user about."""
    row = {}
    for col in feature_cols:
        if col not in active_df.columns:
            continue
        series = active_df[col]
        if pd.api.types.is_numeric_dtype(series):
            row[col] = series.median()
        else:
            mode = series.mode(dropna=True)
            row[col] = mode.iloc[0] if not mode.empty else ""
    return row


def _score(overrides: dict) -> pd.DataFrame:
    """Builds the single-row DataFrame sent to the fitted pipeline: the
    dataset's own median/mode for every modeled feature, overridden by
    whatever the user entered in the form below."""
    row = _baseline_row()
    row.update(overrides)
    return pd.DataFrame([row])[feature_cols]


st.caption(
    f"Scored live with **{best_name}** — the model selected on the Model Evaluation page as best "
    f"for the currently active `{project_opt}` dataset ({len(active_df):,} rows). "
    "Fields not shown below are filled from the dataset's own median/mode."
)


def _download_prediction_button(inputs: dict, results: dict, key: str) -> None:
    """Bonus: downloadable prediction result — the inputs the user entered
    plus the model's output, as a one-row CSV."""
    row = {**inputs, **results, "model_used": best_name, "project_track": project_opt}
    csv_bytes = pd.DataFrame([row]).to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download This Prediction (CSV)", data=csv_bytes,
        file_name=f"{project_opt.lower()}_prediction_result.csv", mime="text/csv", key=key,
    )

if project_opt == "SALES":
    st.markdown("#### Predict Order Profit & Check Margin Floor")
    c1, c2, c3 = st.columns(3)
    sales = c1.number_input("Sales Amount ($):", min_value=5.0, max_value=10000.0, value=350.0, step=10.0)
    quantity = c2.number_input("Order Quantity:", min_value=1, max_value=50, value=3, step=1)
    discount = c3.slider("Promotional Discount:", min_value=0.0, max_value=0.8, value=0.15, step=0.05)

    c4, c5, c6 = st.columns(3)
    shipping_cost = c4.number_input("Shipping Cost ($):", min_value=0.0, max_value=250.0, value=18.5, step=2.5)
    cat_options = sorted(active_df["Category"].dropna().unique().tolist()) if "Category" in active_df.columns else ["Technology", "Office Supplies", "Furniture"]
    region_options = sorted(active_df["Region"].dropna().unique().tolist()) if "Region" in active_df.columns else ["West", "East", "Central", "South"]
    category = c5.selectbox("Product Category:", cat_options)
    region = c6.selectbox("Sales Region:", region_options)

    if st.button("🚀 Calculate Predicted Profit"):
        overrides = {
            "Sales": sales, "Quantity": quantity, "Discount": discount,
            "Shipping_Cost": shipping_cost, "Category": category, "Region": region,
        }
        input_df = _score(overrides)
        try:
            pred_profit = float(comparison["best_pipeline"].predict(input_df)[0])
        except Exception as e:
            st.error(f"Inference failed: {e}")
            st.stop()

        category_label, badge_color = classify_profit(pred_profit)
        st.markdown("---")
        st.subheader("Inference Result")
        st.metric("Predicted Profit", f"${pred_profit:,.2f}", f"Tier: {category_label}")
        if pred_profit < 0.0:
            st.error(
                "🚨 CRITICAL MARGIN LOSS WARNING: This transaction is projected to result in a "
                "negative profit. Examine discount depth and shipping method immediately."
            )
        else:
            st.success(f"Profit Health: Safe margin tier ({category_label}).")
        _download_prediction_button(overrides, {"predicted_profit": pred_profit, "profit_category": category_label}, "dl_sales")

elif project_opt == "CHURN":
    st.markdown("#### Predict Subscriber Churn Risk & Dynamic Threshold")
    threshold = st.slider("Retention Decision Threshold (tau):", min_value=0.10, max_value=0.90, value=0.50, step=0.05)

    c1, c2, c3 = st.columns(3)
    tenure = c1.slider("Tenure (Months):", min_value=1, max_value=72, value=8)
    monthly_charges = c2.number_input("Monthly Charges ($):", min_value=15.0, max_value=150.0, value=85.0)
    contract_options = sorted(active_df["Contract_Type"].dropna().unique().tolist()) if "Contract_Type" in active_df.columns else ["Month-to-month", "One year", "Two year"]
    contract = c3.selectbox("Contract Type:", contract_options)

    c4, c5, c6 = st.columns(3)
    tickets = c4.number_input("Support Tickets (Past 60d):", min_value=0, max_value=15, value=3)
    complaints = c5.number_input("Escalated Complaints:", min_value=0, max_value=10, value=1)
    satisfaction = c6.slider("Satisfaction Score (1-5):", min_value=1, max_value=5, value=2)

    if st.button("🚀 Evaluate Churn Hazard"):
        overrides = {
            "Tenure_Months": tenure, "Monthly_Charges": monthly_charges, "Contract_Type": contract,
            "Support_Tickets": tickets, "Complaints": complaints, "Satisfaction_Score": satisfaction,
        }
        input_df = _score(overrides)
        try:
            prob = float(comparison["best_pipeline"].predict_proba(input_df)[0, 1])
        except Exception as e:
            st.error(f"Inference failed: {e}")
            st.stop()

        tier, color, is_churn = classify_churn_risk(prob, threshold=threshold)
        st.markdown("---")
        st.metric("Churn Probability", f"{prob * 100:.1f}%", f"Tier: {tier}")
        if is_churn:
            st.error(f"🚨 ACTION REQUIRED: Classified as Churn at cutoff {threshold:.2f}. Trigger retention outreach!")
        else:
            st.success(f"✅ Classified as Retained at cutoff {threshold:.2f}.")
        _download_prediction_button(overrides, {"churn_probability": prob, "risk_tier": tier, "threshold": threshold}, "dl_churn")

else:
    # HR Attrition
    st.warning(
        "🛡️ **MANDATORY ETHICAL POLICY**: "
        "This prediction is intended for workforce-level analysis and voluntary retention support. "
        "It must not be used as the sole basis for termination, promotion, salary, disciplinary, or hiring decisions."
    )
    c1, c2, c3 = st.columns(3)
    income = c1.number_input("Monthly Income ($):", min_value=1500, max_value=25000, value=3800)
    years_comp = c2.slider("Years at Company:", min_value=0, max_value=35, value=2)
    overtime = c3.selectbox("Overtime Required:", ["Yes", "No"])

    c4, c5, c6 = st.columns(3)
    wlb = c4.slider("Work-Life Balance (1=Poor, 4=Best):", min_value=1, max_value=4, value=2)
    job_sat = c5.slider("Job Satisfaction (1-4):", min_value=1, max_value=4, value=2)
    dist = c6.number_input("Commute Distance (Miles):", min_value=1, max_value=60, value=18)

    threshold = st.slider("Risk Decision Threshold (tau):", min_value=0.10, max_value=0.90, value=0.50, step=0.05)

    if st.button("🚀 Assess Retention Hazard"):
        overrides = {
            "Monthly_Income": income, "Years_At_Company": years_comp, "Overtime": overtime,
            "Work_Life_Balance": wlb, "Job_Satisfaction": job_sat, "Distance_From_Home": dist,
        }
        input_df = _score(overrides)
        try:
            prob = float(comparison["best_pipeline"].predict_proba(input_df)[0, 1])
        except Exception as e:
            st.error(f"Inference failed: {e}")
            st.stop()

        is_attrition = prob >= threshold
        tier = "Critical Risk" if prob > 0.70 else ("High Risk" if prob > 0.45 else ("Medium Risk" if prob > 0.25 else "Low Risk"))

        st.markdown("---")
        st.metric("Attrition Probability", f"{prob * 100:.1f}%", f"Tier: {tier}")
        if is_attrition:
            st.warning("⚠️ Retention Risk Detected. Schedule proactive voluntary career discussion and review workload/compensation.")
        else:
            st.success("✅ Low departure hazard.")
        _download_prediction_button(overrides, {"attrition_probability": prob, "risk_tier": tier, "threshold": threshold}, "dl_hr")

st.caption(
    "Predictions use the production pipeline trained live on the dataset currently active in the "
    "top navigation bar — switch tracks or upload your own file and this page re-scores against it."
)
