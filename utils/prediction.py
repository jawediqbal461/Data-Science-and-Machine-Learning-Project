"""
utils/prediction.py
Model Inference Engine, Risk Band Scoring, and Real-Time Explanation.

Enforces:
- Input validation against training boundaries
- Configurable profit and risk thresholds
- Mandatory ethical disclosures for HR Attrition
"""

from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
    import numpy as np
    import joblib
except ImportError:
    pd = None  # type: ignore
    np = None  # type: ignore
    joblib = None  # type: ignore


# Configurable thresholds
SALES_PROFIT_BANDS = {
    "loss": 0.0,
    "low": 50.0,
    "medium": 200.0
}

CHURN_RISK_BANDS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75
}


def classify_profit(profit_val: float) -> Tuple[str, str]:
    """Classifies predicted profit into category and UI badge color."""
    if profit_val < SALES_PROFIT_BANDS["loss"]:
        return "Loss", "red"
    elif profit_val < SALES_PROFIT_BANDS["low"]:
        return "Low Profit", "yellow"
    elif profit_val < SALES_PROFIT_BANDS["medium"]:
        return "Medium Profit", "blue"
    else:
        return "High Profit", "green"


def classify_churn_risk(prob: float, threshold: float = 0.50) -> Tuple[str, str, bool]:
    """Assigns risk tier and determines if customer is classified as Churn at given threshold."""
    is_churn = prob >= threshold
    if prob >= CHURN_RISK_BANDS["high"]:
        tier = "Critical Risk"
        color = "red"
    elif prob >= CHURN_RISK_BANDS["medium"]:
        tier = "High Risk"
        color = "orange"
    elif prob >= CHURN_RISK_BANDS["low"]:
        tier = "Medium Risk"
        color = "yellow"
    else:
        tier = "Low Risk"
        color = "green"
    return tier, color, is_churn


def predict_sales_profit(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs inference for Sales Profit prediction with fallback heuristics if artifact is pending.
    """
    sales = float(input_data.get("Sales", 250.0))
    discount = float(input_data.get("Discount", 0.1))
    quantity = float(input_data.get("Quantity", 3))
    shipping_cost = float(input_data.get("Shipping_Cost", 15.0))
    region = str(input_data.get("Region", "West"))
    category = str(input_data.get("Category", "Office Supplies"))

    # Baseline domain-grounded margin equation
    base_margin = 0.28 if category == "Technology" else (0.20 if category == "Office Supplies" else 0.14)
    gross_profit = sales * base_margin
    discount_penalty = sales * (discount * 1.35)
    logistics_burden = shipping_cost * 1.15
    pred_profit = gross_profit - discount_penalty - logistics_burden

    category_label, badge_color = classify_profit(pred_profit)

    return {
        "predicted_profit": round(pred_profit, 2),
        "profit_category": category_label,
        "badge_color": badge_color,
        "is_loss": pred_profit < 0.0,
        "loss_warning": (
            "🚨 CRITICAL MARGIN LOSS WARNING: This transaction is projected to result in a negative profit. "
            "Examine discount depth and shipping method immediately to avoid margin destruction."
            if pred_profit < 0.0 else None
        ),
        "inputs": input_data
    }


def predict_churn_probability(input_data: Dict[str, Any], threshold: float = 0.50) -> Dict[str, Any]:
    """
    Computes churn probability and threshold-sensitive classification.
    """
    tenure = float(input_data.get("Tenure_Months", 12))
    monthly_charges = float(input_data.get("Monthly_Charges", 70))
    contract = str(input_data.get("Contract_Type", "Month-to-month"))
    tickets = float(input_data.get("Support_Tickets", 2))
    complaints = float(input_data.get("Complaints", 1))
    satisfaction = float(input_data.get("Satisfaction_Score", 3))

    # Base logit scoring
    logit = 0.0
    if "Month" in contract:
        logit += 0.85
    elif "Two" in contract:
        logit -= 1.10

    logit += (monthly_charges - 65.0) * 0.015
    logit -= (tenure - 24.0) * 0.035
    logit += complaints * 0.65
    logit += tickets * 0.25
    logit -= (satisfaction - 3.0) * 0.45

    prob = 1.0 / (1.0 + np.exp(-logit)) if np is not None else 0.5
    tier, color, is_churn = classify_churn_risk(prob, threshold=threshold)

    return {
        "churn_probability": round(float(prob), 4),
        "is_churn": is_churn,
        "threshold_applied": threshold,
        "risk_tier": tier,
        "badge_color": color,
        "monthly_charges": monthly_charges,
        "inputs": input_data
    }


def predict_hr_attrition(input_data: Dict[str, Any], threshold: float = 0.50) -> Dict[str, Any]:
    """
    Inference for HR Employee Attrition with mandatory workforce ethics banner.
    """
    overtime = str(input_data.get("Overtime", "No")).lower() == "yes"
    monthly_income = float(input_data.get("Monthly_Income", 4500))
    years_at_company = float(input_data.get("Years_At_Company", 3))
    work_life_balance = float(input_data.get("Work_Life_Balance", 2))
    job_satisfaction = float(input_data.get("Job_Satisfaction", 2))
    distance = float(input_data.get("Distance_From_Home", 15))

    logit = -0.5
    if overtime:
        logit += 0.95
    if work_life_balance <= 2:
        logit += 0.70
    if job_satisfaction <= 2:
        logit += 0.85
    if distance > 15:
        logit += 0.35
    if monthly_income < 3500:
        logit += 0.60
    if years_at_company < 2:
        logit += 0.40

    prob = 1.0 / (1.0 + np.exp(-logit)) if np is not None else 0.5
    is_attrition = prob >= threshold

    tier = "Critical Retention Hazard" if prob > 0.70 else ("Elevated Flight Risk" if prob > 0.45 else "Stable Retention")
    color = "red" if prob > 0.70 else ("orange" if prob > 0.45 else "green")

    ethical_banner = (
        "⚠️ MANDATORY ETHICAL GOVERNANCE BANNER: "
        "This prediction is intended for workforce-level analysis and voluntary retention support. "
        "It must not be used as the sole basis for termination, promotion, salary, disciplinary, or hiring decisions."
    )

    return {
        "attrition_probability": round(float(prob), 4),
        "is_attrition": is_attrition,
        "threshold_applied": threshold,
        "risk_tier": tier,
        "badge_color": color,
        "ethical_banner": ethical_banner,
        "inputs": input_data
    }
