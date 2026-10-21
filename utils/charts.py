"""
utils/charts.py
Reusable Visualization Chart Factory.

Standardized styling:
- Consistent corporate color palette
- Clear titles and readable axis labels
- Non-causal observation captions
- Works with Plotly or Matplotlib/Seaborn
"""

from typing import Any, Dict, List, Optional

CHART_PALETTE = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"]

# Metadata for charts per project track
EDA_CHARTS_CATALOG = {
    "SALES": [
        {"id": "CHART_S1", "title": "Profit Distribution & Margin Density", "type": "histogram", "caption": "Shows distribution of order profits ranging from negative margin loss orders to high-value transactions."},
        {"id": "CHART_S2", "title": "Discount Depth vs Net Realized Profit", "type": "scatter", "caption": "Highlights the inflection point where discount rates exceeding 20% drag transaction profits into negative territory."},
        {"id": "CHART_S3", "title": "Profit Margin by Product Category & Sub-Category", "type": "bar", "caption": "Compares Technology, Office Supplies, and Furniture profitability contributions."},
        {"id": "CHART_S4", "title": "Shipping Cost Ratio by Ship Mode", "type": "box", "caption": "Illustrates logistics overhead variance across First Class, Same Day, and Standard delivery modes."},
        {"id": "CHART_S5", "title": "Regional Sales & Profit Comparison", "type": "grouped_bar", "caption": "Identifies regional discrepancies with South underperforming East and West zones."},
        {"id": "CHART_S6", "title": "Order Quantity Binned vs Total Realized Margin", "type": "bar", "caption": "Shows volume purchasing behaviors and wholesale margin realization."},
        {"id": "CHART_S7", "title": "Correlation Matrix Heatmap", "type": "heatmap", "caption": "Evaluates linear correlation among numerical transaction features (Sales, Discount, Shipping, Profit)."},
        {"id": "CHART_S8", "title": "Actual vs Predicted Profit Scatter", "type": "scatter_fit", "caption": "Assesses model fit accuracy against the 45-degree identity reference line."},
        {"id": "CHART_S9", "title": "Regression Residuals Distribution", "type": "residual", "caption": "Validates residual normality and checks for homoscedasticity across predicted profit scales."},
        {"id": "CHART_S10", "title": "Feature Importance Ranking", "type": "horizontal_bar", "caption": "Ranks feature predictive weight, confirming Discount and Unit Price as top profit drivers."}
    ],
    "CHURN": [
        {"id": "CHART_C1", "title": "Overall Customer Churn Rate Distribution", "type": "donut", "caption": "Shows ratio of retained (73.5%) versus churned (26.5%) subscribers."},
        {"id": "CHART_C2", "title": "Churn Rate by Contract Type", "type": "bar", "caption": "Illustrates that Month-to-month contracts experience over 3x higher churn than 1- or 2-year commitments."},
        {"id": "CHART_C3", "title": "Monthly Charges vs Churn Probability", "type": "kde", "caption": "Highlights elevated attrition among accounts paying above $75 per billing cycle."},
        {"id": "CHART_C4", "title": "Customer Tenure (Months) vs Retention", "type": "histogram", "caption": "Demonstrates the initial 12-month vulnerability cliff where early cancellations concentrate."},
        {"id": "CHART_C5", "title": "Support Ticket Velocity vs Cancellation", "type": "scatter", "caption": "Shows sharp attrition escalation when unresolved support requests exceed 2 tickets."},
        {"id": "CHART_C6", "title": "Add-On Security & Tech Support Adoption Impact", "type": "bar", "caption": "Compares churn incidence across users with vs without digital support add-ons."},
        {"id": "CHART_C7", "title": "Payment Method Breakdown & Churn Risk", "type": "bar", "caption": "Demonstrates higher attrition among electronic check payers compared to credit card auto-pay."},
        {"id": "CHART_C8", "title": "Feature Correlation Heatmap", "type": "heatmap", "caption": "Quantifies relationships between charges, complaints, tenure, and churn status."},
        {"id": "CHART_C9", "title": "Model Comparison: ROC Curves", "type": "roc_curve", "caption": "Compares True Positive vs False Positive trade-offs across all 5 evaluated classifiers."},
        {"id": "CHART_C10", "title": "Confusion Matrix at Default vs Tuned Threshold", "type": "confusion_matrix", "caption": "Examines True Positives, True Negatives, False Positives, and False Negatives."}
    ],
    "HR_ATTRITION": [
        {"id": "CHART_H1", "title": "Workforce Attrition Proportion", "type": "donut", "caption": "Displays current organizational baseline attrition rate (16.2%)."},
        {"id": "CHART_H2", "title": "Overtime vs Attrition Rate", "type": "bar", "caption": "Reveals that employees working overtime experience 31.8% attrition vs 10.4% without overtime."},
        {"id": "CHART_H3", "title": "Monthly Income Distribution by Attrition Status", "type": "box", "caption": "Demonstrates salary distribution compression in junior and exiting employee bands."},
        {"id": "CHART_H4", "title": "Attrition by Department and Job Role", "type": "grouped_bar", "caption": "Highlights elevated departures in Sales Representatives and Laboratory Technicians."},
        {"id": "CHART_H5", "title": "Years in Current Role vs Organizational Tenure", "type": "scatter", "caption": "Illustrates the role stagnation cliff where tenure beyond 4 years without promotion elevates turnover."},
        {"id": "CHART_H6", "title": "Work-Life Balance & Job Satisfaction Matrix", "type": "heatmap", "caption": "Maps joint distribution of employee morale against departure hazard."},
        {"id": "CHART_H7", "title": "Commute Distance (Miles) vs Flight Risk", "type": "kde", "caption": "Shows elevated departure frequency for employees commuting greater than 18 miles."},
        {"id": "CHART_H8", "title": "Work Mode Attrition: Remote vs Hybrid vs On-site", "type": "bar", "caption": "Compares turnover rates across flexible and co-located working arrangements."},
        {"id": "CHART_H9", "title": "Missing Value Strategy Performance Comparison", "type": "bar", "caption": "Evaluates F1 and Recall across row-drop, mean, median, and mode imputation strategies."},
        {"id": "CHART_H10", "title": "Subgroup Equity & Demographic Parity Review", "type": "audit_bar", "caption": "Audits model recall and False Positive Rate across gender, age groups, and departments."},
        {"id": "CHART_H11", "title": "5-Fold Cross Validation Score Stability", "type": "box", "caption": "Validates model stability across independent cross-validation splits (mean F1: 0.858)."},
        {"id": "CHART_H12", "title": "Feature Importance Hierarchy (Random Forest)", "type": "horizontal_bar", "caption": "Confirms Overtime, Monthly Income, Role Stagnation, and Job Satisfaction as top predictors."}
    ]
}
