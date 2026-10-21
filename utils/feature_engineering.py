"""
utils/feature_engineering.py
Domain Feature Engineering Engines for Sales, Churn, and HR Attrition.

Every engineered feature documents:
- Mathematical formula
- Business domain rationale
- Data leakage safety check
- Division by zero guard (epsilon = 1e-6 or np.where)
"""

from typing import Any, Dict, List, Tuple

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None  # type: ignore
    np = None  # type: ignore


# Documented specifications for all engineered features
FEATURE_CATALOG = {
    "SALES": [
        {
            "name": "Discount_Per_Quantity",
            "formula": "Discount / (Quantity + 1e-6)",
            "business_meaning": "Effective promotional discount intensity per physical unit ordered.",
            "leakage_safe": True,
            "leakage_notes": "Known at checkout time before fulfillment."
        },
        {
            "name": "Shipping_Cost_Ratio",
            "formula": "Shipping_Cost / (Sales + 1e-6)",
            "business_meaning": "Logistics cost burden as percentage of top-line revenue.",
            "leakage_safe": True,
            "leakage_notes": "Calculated upon shipping method selection."
        },
        {
            "name": "Unit_Price_Effective",
            "formula": "(Sales / (Quantity + 1e-6)) * (1 - Discount)",
            "business_meaning": "Realized revenue per unit after promotional price discounting.",
            "leakage_safe": True,
            "leakage_notes": "Known at order submission time."
        },
        {
            "name": "Margin_Pressure_Index",
            "formula": "(Discount * 100) + (Shipping_Cost / (Sales + 1e-6) * 50)",
            "business_meaning": "Composite stress score combining discount erosion and freight costs.",
            "leakage_safe": True,
            "leakage_notes": "Purely pre-completion order characteristics."
        },
        {
            "name": "Order_Volume_Category",
            "formula": "Binned Quantity: Low (1-2), Medium (3-5), Bulk (>5)",
            "business_meaning": "Captures volume pricing tiers and wholesale order behaviors.",
            "leakage_safe": True,
            "leakage_notes": "Known immediately upon order placement."
        }
    ],
    "CHURN": [
        {
            "name": "Charges_Per_Tenure_Ratio",
            "formula": "Total_Charges / (Tenure_Months + 1.0)",
            "business_meaning": "Average historical monthly expenditure normalized by loyalty tenure.",
            "leakage_safe": True,
            "leakage_notes": "Reflects account history up to prediction cutoff."
        },
        {
            "name": "Ticket_Velocity",
            "formula": "Support_Tickets / (Tenure_Months + 1.0)",
            "business_meaning": "Support friction frequency per month of active subscription.",
            "leakage_safe": True,
            "leakage_notes": "Accumulated before churn event."
        },
        {
            "name": "Friction_Score",
            "formula": "(Complaints * 2.5) + (Support_Tickets * 1.0) - (Satisfaction_Score * 0.8)",
            "business_meaning": "Combined customer frustration index factoring complaints and sentiment.",
            "leakage_safe": True,
            "leakage_notes": "Survey and CRM metrics from current billing cycle."
        },
        {
            "name": "High_Risk_Contract_Flag",
            "formula": "1 if Contract == 'Month-to-month' and Monthly_Charges > 70 else 0",
            "business_meaning": "Identifies price-sensitive subscribers lacking long-term contractual commitment.",
            "leakage_safe": True,
            "leakage_notes": "Current subscription terms."
        },
        {
            "name": "Digital_Engagement_Index",
            "formula": "(Paperless_Billing + Tech_Support + Online_Security) / 3.0",
            "business_meaning": "Depth of digital service adoption and stickiness.",
            "leakage_safe": True,
            "leakage_notes": "Active add-on services."
        }
    ],
    "HR_ATTRITION": [
        {
            "name": "Income_Per_Tenure_Year",
            "formula": "Monthly_Income / (Years_At_Company + 1.0)",
            "business_meaning": "Compensation accumulation rate relative to organizational tenure.",
            "leakage_safe": True,
            "leakage_notes": "Current compensation and tenure."
        },
        {
            "name": "Role_Stagnation_Index",
            "formula": "Years_In_Current_Role / (Years_At_Company + 1.0)",
            "business_meaning": "Proportion of company career spent in same job without internal mobility.",
            "leakage_safe": True,
            "leakage_notes": "Historical job history."
        },
        {
            "name": "Overtime_Burnout_Flag",
            "formula": "1 if Overtime == 'Yes' and Work_Life_Balance <= 2 else 0",
            "business_meaning": "Severe burnout hazard flag from persistent overtime with low life balance.",
            "leakage_safe": True,
            "leakage_notes": "Annual pulse survey & timesheet data."
        },
        {
            "name": "Satisfaction_Deficit",
            "formula": "(4 - Job_Satisfaction) + (4 - Environment_Satisfaction)",
            "business_meaning": "Cumulative workplace dissatisfaction gap across role and culture.",
            "leakage_safe": True,
            "leakage_notes": "Latest internal survey responses."
        },
        {
            "name": "Commute_Burden_Ratio",
            "formula": "Distance_From_Home / (Monthly_Income / 1000.0 + 1.0)",
            "business_meaning": "Commute hardship weighed against income adequacy.",
            "leakage_safe": True,
            "leakage_notes": "Employee residential profile."
        },
        {
            "name": "Career_Velocity",
            "formula": "Job_Level / (Total_Working_Years + 1.0)",
            "business_meaning": "Promotional trajectory speed across total professional career.",
            "leakage_safe": True,
            "leakage_notes": "Seniority versus experience."
        },
        {
            "name": "Job_Hopping_Propensity",
            "formula": "Num_Companies_Worked / (Total_Working_Years + 1.0)",
            "business_meaning": "Historical willingness to transition between employers.",
            "leakage_safe": True,
            "leakage_notes": "Resume prior history."
        },
        {
            "name": "Remote_Isolation_Risk",
            "formula": "1 if Work_Mode == 'Remote' and Job_Satisfaction <= 2 else 0",
            "business_meaning": "Detachment risk for isolated telecommuters with declining morale.",
            "leakage_safe": True,
            "leakage_notes": "Current workplace arrangement."
        }
    ]
}


def engineer_features(df: Any, project_option: str = "SALES") -> Any:
    """Applies domain-specific feature engineering with division-by-zero guards."""
    if pd is None or not isinstance(df, pd.DataFrame):
        return df

    data = df.copy()
    eps = 1e-6

    if project_option == "SALES":
        if "Order_Date" in data.columns:
            order_dt = pd.to_datetime(data["Order_Date"], errors="coerce")
            data["Order_Year"] = order_dt.dt.year
            data["Order_Month"] = order_dt.dt.month
            data["Month_Name"] = order_dt.dt.strftime("%b")
            data["Quarter"] = order_dt.dt.quarter
            data["Day_Name"] = order_dt.dt.day_name()
        if "Discount" in data.columns and "Quantity" in data.columns:
            data["Discount_Per_Quantity"] = data["Discount"] / (data["Quantity"] + eps)
        if "Shipping_Cost" in data.columns and "Sales" in data.columns:
            data["Shipping_Cost_Ratio"] = data["Shipping_Cost"] / (data["Sales"] + eps)
        if "Sales" in data.columns and "Quantity" in data.columns and "Discount" in data.columns:
            data["Unit_Price_Effective"] = (data["Sales"] / (data["Quantity"] + eps)) * (1.0 - data["Discount"])
        if "Discount" in data.columns and "Shipping_Cost" in data.columns and "Sales" in data.columns:
            data["Margin_Pressure_Index"] = (data["Discount"] * 100.0) + (data["Shipping_Cost"] / (data["Sales"] + eps) * 50.0)
        if "Quantity" in data.columns:
            data["Order_Volume_Category"] = pd.cut(
                data["Quantity"],
                bins=[-np.inf, 2, 5, np.inf],
                labels=["Low_Volume", "Medium_Volume", "Bulk_Volume"]
            )

    elif project_option == "CHURN":
        if "Total_Charges" in data.columns and "Tenure_Months" in data.columns:
            data["Charges_Per_Tenure_Ratio"] = data["Total_Charges"] / (data["Tenure_Months"] + 1.0)
        if "Support_Tickets" in data.columns and "Tenure_Months" in data.columns:
            data["Ticket_Velocity"] = data["Support_Tickets"] / (data["Tenure_Months"] + 1.0)
        if "Complaints" in data.columns and "Support_Tickets" in data.columns and "Satisfaction_Score" in data.columns:
            data["Friction_Score"] = (data["Complaints"] * 2.5) + (data["Support_Tickets"] * 1.0) - (data["Satisfaction_Score"] * 0.8)
        if "Contract_Type" in data.columns and "Monthly_Charges" in data.columns:
            data["High_Risk_Contract_Flag"] = (
                (data["Contract_Type"].astype(str).str.contains("Month", case=False)) &
                (data["Monthly_Charges"] > 70.0)
            ).astype(int)
        tech_col = data.get("Tech_Support", 0)
        sec_col = data.get("Online_Security", 0)
        paper_col = data.get("Paperless_Billing", 0)
        # Convert binary if object
        t_val = (tech_col == "Yes").astype(int) if hasattr(tech_col, "map") else 0
        s_val = (sec_col == "Yes").astype(int) if hasattr(sec_col, "map") else 0
        p_val = (paper_col == "Yes").astype(int) if hasattr(paper_col, "map") else 0
        data["Digital_Engagement_Index"] = (t_val + s_val + p_val) / 3.0

    elif project_option == "HR_ATTRITION":
        if "Monthly_Income" in data.columns and "Years_At_Company" in data.columns:
            data["Income_Per_Tenure_Year"] = data["Monthly_Income"] / (data["Years_At_Company"] + 1.0)
        if "Years_In_Current_Role" in data.columns and "Years_At_Company" in data.columns:
            data["Role_Stagnation_Index"] = data["Years_In_Current_Role"] / (data["Years_At_Company"] + 1.0)
        if "Overtime" in data.columns and "Work_Life_Balance" in data.columns:
            data["Overtime_Burnout_Flag"] = (
                (data["Overtime"].astype(str).str.lower() == "yes") &
                (pd.to_numeric(data["Work_Life_Balance"], errors="coerce") <= 2)
            ).astype(int)
        if "Job_Satisfaction" in data.columns and "Environment_Satisfaction" in data.columns:
            js = pd.to_numeric(data["Job_Satisfaction"], errors="coerce").fillna(3)
            es = pd.to_numeric(data["Environment_Satisfaction"], errors="coerce").fillna(3)
            data["Satisfaction_Deficit"] = (4 - js) + (4 - es)
        if "Distance_From_Home" in data.columns and "Monthly_Income" in data.columns:
            dist = pd.to_numeric(data["Distance_From_Home"], errors="coerce").fillna(10)
            inc = pd.to_numeric(data["Monthly_Income"], errors="coerce").fillna(4000)
            data["Commute_Burden_Ratio"] = dist / (inc / 1000.0 + 1.0)
        if "Job_Level" in data.columns and "Total_Working_Years" in data.columns:
            jl = pd.to_numeric(data["Job_Level"], errors="coerce").fillna(2)
            tw = pd.to_numeric(data["Total_Working_Years"], errors="coerce").fillna(5)
            data["Career_Velocity"] = jl / (tw + 1.0)
        if "Num_Companies_Worked" in data.columns and "Total_Working_Years" in data.columns:
            nc = pd.to_numeric(data["Num_Companies_Worked"], errors="coerce").fillna(2)
            tw = pd.to_numeric(data["Total_Working_Years"], errors="coerce").fillna(5)
            data["Job_Hopping_Propensity"] = nc / (tw + 1.0)
        if "Work_Mode" in data.columns and "Job_Satisfaction" in data.columns:
            wm = data["Work_Mode"].astype(str).str.lower() == "remote"
            js = pd.to_numeric(data["Job_Satisfaction"], errors="coerce").fillna(3) <= 2
            data["Remote_Isolation_Risk"] = (wm & js).astype(int)

    return data
