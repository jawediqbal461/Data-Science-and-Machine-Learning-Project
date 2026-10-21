"""
pages/5_Predictive_Inference.py
Real-Time Inference Engine with Input Validation and Risk Band Scoring.
"""

import streamlit as st
from utils.prediction import (
    predict_sales_profit,
    predict_churn_probability,
    predict_hr_attrition
)

st.set_page_config(page_title="Predictive Inference Engine", page_icon="🔮", layout="wide")
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"🔮 Real-Time Predictive Inference: {project_opt}")

if project_opt == "SALES":
    st.markdown("#### Predict Order Profit & Check Margin Floor")
    c1, c2, c3 = st.columns(3)
    sales = c1.number_input("Sales Amount ($):", min_value=5.0, max_value=10000.0, value=350.0, step=10.0)
    quantity = c2.number_input("Order Quantity:", min_value=1, max_value=50, value=3, step=1)
    discount = c3.slider("Promotional Discount:", min_value=0.0, max_value=0.8, value=0.15, step=0.05)

    c4, c5, c6 = st.columns(3)
    shipping_cost = c4.number_input("Shipping Cost ($):", min_value=0.0, max_value=250.0, value=18.5, step=2.5)
    category = c5.selectbox("Product Category:", ["Technology", "Office Supplies", "Furniture"])
    region = c6.selectbox("Sales Region:", ["West", "East", "Central", "South"])

    if st.button("🚀 Calculate Predicted Profit"):
        res = predict_sales_profit({
            "Sales": sales, "Quantity": quantity, "Discount": discount,
            "Shipping_Cost": shipping_cost, "Category": category, "Region": region
        })
        st.markdown("---")
        st.subheader("Inference Result")
        st.metric("Predicted Profit", f"${res['predicted_profit']:,.2f}", f"Tier: {res['profit_category']}")
        if res["is_loss"]:
            st.error(res["loss_warning"])
        else:
            st.success(f"Profit Health: Safe margin tier ({res['profit_category']}).")

elif project_opt == "CHURN":
    st.markdown("#### Predict Subscriber Churn Risk & Dynamic Threshold")
    threshold = st.slider("Retention Decision Threshold (tau):", min_value=0.10, max_value=0.90, value=0.50, step=0.05)
    
    c1, c2, c3 = st.columns(3)
    tenure = c1.slider("Tenure (Months):", min_value=1, max_value=72, value=8)
    monthly_charges = c2.number_input("Monthly Charges ($):", min_value=15.0, max_value=150.0, value=85.0)
    contract = c3.selectbox("Contract Type:", ["Month-to-month", "One year", "Two year"])

    c4, c5, c6 = st.columns(3)
    tickets = c4.number_input("Support Tickets (Past 60d):", min_value=0, max_value=15, value=3)
    complaints = c5.number_input("Escalated Complaints:", min_value=0, max_value=10, value=1)
    satisfaction = c6.slider("Satisfaction Score (1-5):", min_value=1, max_value=5, value=2)

    if st.button("🚀 Evaluate Churn Hazard"):
        res = predict_churn_probability({
            "Tenure_Months": tenure, "Monthly_Charges": monthly_charges, "Contract_Type": contract,
            "Support_Tickets": tickets, "Complaints": complaints, "Satisfaction_Score": satisfaction
        }, threshold=threshold)
        st.markdown("---")
        p = res["churn_probability"]
        st.metric("Churn Probability", f"{p * 100:.1f}%", f"Tier: {res['risk_tier']}")
        if res["is_churn"]:
            st.error(f"🚨 ACTION REQUIRED: Classified as Churn at cutoff {threshold:.2f}. Trigger retention outreach!")
        else:
            st.success(f"✅ Classified as Retained at cutoff {threshold:.2f}.")

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

    if st.button("🚀 Assess Retention Hazard"):
        res = predict_hr_attrition({
            "Monthly_Income": income, "Years_At_Company": years_comp, "Overtime": overtime,
            "Work_Life_Balance": wlb, "Job_Satisfaction": job_sat, "Distance_From_Home": dist
        })
        st.markdown("---")
        prob = res["attrition_probability"]
        st.metric("Attrition Probability", f"{prob * 100:.1f}%", f"Tier: {res['risk_tier']}")
        if res["is_attrition"]:
            st.warning(f"⚠️ Retention Risk Detected. Schedule proactive voluntary career discussion.")
        else:
            st.success(f"✅ Low departure hazard.")
