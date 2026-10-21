"""
utils/charts.py
Reusable Visualization Chart Factory.

Builds real, data-driven Plotly figures for the Analytics Dashboard.
Every chart is computed from the actual bundled dataset for the active
project track (SALES / CHURN / HR_ATTRITION); chart-specific ML diagnostics
(feature importance, ROC curves, confusion matrices, CV stability) are
produced by quickly training the same model families documented in
utils/modeling.py against the loaded data.

Standardized styling:
- Consistent corporate color palette
- Clear titles and readable axis labels
- Non-causal observation captions
- Dark theme to match the app's Streamlit theme
"""

from typing import Any, Dict, List, Optional

try:
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import (
        RandomForestRegressor,
        RandomForestClassifier,
        GradientBoostingClassifier,
    )
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import roc_curve, auc, confusion_matrix, recall_score
except ImportError:  # pragma: no cover - defensive import guard
    np = None  # type: ignore
    pd = None  # type: ignore
    px = None  # type: ignore
    go = None  # type: ignore

from utils.modeling import build_preprocessor
from utils.preprocessing import EXCLUSION_RULES, run_missing_value_strategies

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
        {"id": "CHART_C1", "title": "Overall Customer Churn Rate Distribution", "type": "donut", "caption": "Shows ratio of retained versus churned subscribers in the active dataset."},
        {"id": "CHART_C2", "title": "Churn Rate by Contract Type", "type": "bar", "caption": "Illustrates that Month-to-month contracts experience markedly higher churn than 1- or 2-year commitments."},
        {"id": "CHART_C3", "title": "Monthly Charges vs Churn Probability", "type": "kde", "caption": "Highlights elevated attrition among accounts paying above-average billing amounts per cycle."},
        {"id": "CHART_C4", "title": "Customer Tenure (Months) vs Retention", "type": "histogram", "caption": "Demonstrates the early-tenure vulnerability window where cancellations concentrate."},
        {"id": "CHART_C5", "title": "Support Ticket Velocity vs Cancellation", "type": "scatter", "caption": "Shows attrition escalation as unresolved support requests increase."},
        {"id": "CHART_C6", "title": "Add-On Security & Tech Support Adoption Impact", "type": "bar", "caption": "Compares churn incidence across users with vs without digital support add-ons."},
        {"id": "CHART_C7", "title": "Payment Method Breakdown & Churn Risk", "type": "bar", "caption": "Demonstrates differing attrition rates across payment methods."},
        {"id": "CHART_C8", "title": "Feature Correlation Heatmap", "type": "heatmap", "caption": "Quantifies relationships between charges, complaints, tenure, and churn status."},
        {"id": "CHART_C9", "title": "Model Comparison: ROC Curves", "type": "roc_curve", "caption": "Compares True Positive vs False Positive trade-offs across the evaluated classifiers."},
        {"id": "CHART_C10", "title": "Confusion Matrix at Default vs Tuned Threshold", "type": "confusion_matrix", "caption": "Examines True Positives, True Negatives, False Positives, and False Negatives at both thresholds."}
    ],
    "HR_ATTRITION": [
        {"id": "CHART_H1", "title": "Workforce Attrition Proportion", "type": "donut", "caption": "Displays current organizational baseline attrition rate."},
        {"id": "CHART_H2", "title": "Overtime vs Attrition Rate", "type": "bar", "caption": "Reveals the gap in attrition between employees working overtime and those who do not."},
        {"id": "CHART_H3", "title": "Monthly Income Distribution by Attrition Status", "type": "box", "caption": "Demonstrates salary distribution compression in junior and exiting employee bands."},
        {"id": "CHART_H4", "title": "Attrition by Department and Job Role", "type": "grouped_bar", "caption": "Highlights elevated departures across department and job-role combinations."},
        {"id": "CHART_H5", "title": "Years in Current Role vs Organizational Tenure", "type": "scatter", "caption": "Illustrates the role stagnation cliff where tenure without role change elevates turnover."},
        {"id": "CHART_H6", "title": "Work-Life Balance & Job Satisfaction Matrix", "type": "heatmap", "caption": "Maps joint distribution of employee morale against departure hazard."},
        {"id": "CHART_H7", "title": "Commute Distance (Miles) vs Flight Risk", "type": "kde", "caption": "Shows elevated departure frequency for employees with longer commutes."},
        {"id": "CHART_H8", "title": "Work Mode Attrition: Remote vs Hybrid vs On-site", "type": "bar", "caption": "Compares turnover rates across flexible and co-located working arrangements."},
        {"id": "CHART_H9", "title": "Missing Value Strategy Performance Comparison", "type": "bar", "caption": "Evaluates F1 and Recall across row-drop, mean, median, and mode imputation strategies."},
        {"id": "CHART_H10", "title": "Subgroup Equity & Demographic Parity Review", "type": "audit_bar", "caption": "Audits model recall across gender subgroups on the held-out test fold."},
        {"id": "CHART_H11", "title": "5-Fold Cross Validation Score Stability", "type": "box", "caption": "Validates model stability across independent cross-validation splits."},
        {"id": "CHART_H12", "title": "Feature Importance Hierarchy (Random Forest)", "type": "horizontal_bar", "caption": "Confirms the top predictors driving attrition risk."}
    ]
}


def _dark_layout(fig: Any, height: int = 420) -> Any:
    """Applies a consistent dark, transparent theme matching the app."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        font=dict(color="#F8FAFC"),
    )
    return fig


def _clean_feature_name(name: str) -> str:
    for prefix in ("num__", "cat__", "remainder__"):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


def _xy_split(df: "pd.DataFrame", project_option: str):
    """Splits a dataframe into (X, y, numeric_features, categorical_features) per EXCLUSION_RULES."""
    rules = EXCLUSION_RULES[project_option]
    target_col = rules["target"]
    drop_cols = rules["id_cols"] + rules["post_completion_leakage"] + [target_col]
    feature_cols = [c for c in df.columns if c not in drop_cols]

    X = df[feature_cols].copy()
    y = df[target_col].copy()
    numeric_features = list(X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns)
    categorical_features = list(X.select_dtypes(include=["object", "category", "bool"]).columns)
    return X, y, numeric_features, categorical_features


def train_primary_model(df: "pd.DataFrame", project_option: str) -> Dict[str, Any]:
    """Trains the production model family for the track and returns diagnostics
    used by the actual-vs-predicted, residual, and feature-importance charts."""
    X, y, numeric_features, categorical_features = _xy_split(df, project_option)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    is_classification = project_option in ("CHURN", "HR_ATTRITION")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y if is_classification else None
    )

    if project_option == "SALES":
        estimator = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    elif project_option == "CHURN":
        estimator = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
    else:
        estimator = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)

    from sklearn.pipeline import Pipeline
    pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    probs = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None

    try:
        feat_names = [_clean_feature_name(n) for n in pipe.named_steps["preprocessor"].get_feature_names_out()]
    except Exception:
        feat_names = [f"feature_{i}" for i in range(len(pipe.named_steps["model"].feature_importances_))]
    importances = pipe.named_steps["model"].feature_importances_

    return {
        "pipeline": pipe,
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
        "preds": preds, "probs": probs,
        "feature_names": feat_names, "importances": importances,
    }


def train_classifier_suite(df: "pd.DataFrame", project_option: str) -> Dict[str, Any]:
    """Trains the comparison classifier suite for ROC-curve charts (CHURN track)."""
    X, y, numeric_features, categorical_features = _xy_split(df, project_option)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=7, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=7),
    }

    from sklearn.pipeline import Pipeline
    roc_data = {}
    for name, est in models.items():
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", est)])
        pipe.fit(X_train, y_train)
        probs = pipe.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_data[name] = {"fpr": fpr, "tpr": tpr, "auc": auc(fpr, tpr)}

    return {"roc_data": roc_data, "y_test": y_test}


def run_cross_validation(df: "pd.DataFrame", project_option: str) -> List[float]:
    """Runs 5-fold stratified cross-validation for the production classifier (HR track)."""
    X, y, numeric_features, categorical_features = _xy_split(df, project_option)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    estimator = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)

    from sklearn.pipeline import Pipeline
    pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipe, X, y, cv=cv, scoring="f1")
    return list(scores)


# ---------------------------------------------------------------------------
# SALES chart builders
# ---------------------------------------------------------------------------

def _s1_profit_histogram(df):
    fig = px.histogram(df, x="Profit", nbins=30, color_discrete_sequence=[CHART_PALETTE[0]])
    fig.add_vline(x=0, line_dash="dash", line_color=CHART_PALETTE[3])
    return _dark_layout(fig)


def _s2_discount_vs_profit(df):
    fig = px.scatter(
        df, x="Discount", y="Profit", color="Category",
        color_discrete_sequence=CHART_PALETTE, opacity=0.75,
    )
    fig.add_vline(x=0.20, line_dash="dash", line_color=CHART_PALETTE[3],
                  annotation_text="20% discount threshold")
    return _dark_layout(fig)


def _s3_profit_by_category(df):
    grouped = df.groupby(["Category", "Sub_Category"], as_index=False)["Profit"].mean()
    fig = px.bar(grouped, x="Sub_Category", y="Profit", color="Category",
                 color_discrete_sequence=CHART_PALETTE, barmode="group")
    fig.update_xaxes(tickangle=-35)
    return _dark_layout(fig)


def _s4_shipping_ratio_by_mode(df):
    ratio_df = df.copy()
    ratio_df["Shipping_Ratio"] = ratio_df["Shipping_Cost"] / ratio_df["Sales"].replace(0, np.nan)
    fig = px.box(ratio_df, x="Ship_Mode", y="Shipping_Ratio", color="Ship_Mode",
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(showlegend=False)
    return _dark_layout(fig)


def _s5_regional_sales_profit(df):
    grouped = df.groupby("Region", as_index=False)[["Sales", "Profit"]].sum()
    melted = grouped.melt(id_vars="Region", value_vars=["Sales", "Profit"], var_name="Metric", value_name="Amount")
    fig = px.bar(melted, x="Region", y="Amount", color="Metric", barmode="group",
                 color_discrete_sequence=CHART_PALETTE)
    return _dark_layout(fig)


def _s6_quantity_binned_margin(df):
    bins = [0, 2, 4, 6, 8, df["Quantity"].max() + 1]
    labels = ["1-2", "3-4", "5-6", "7-8", "9+"]
    binned = df.copy()
    binned["Quantity_Bin"] = pd.cut(binned["Quantity"], bins=bins, labels=labels, right=True, include_lowest=True)
    grouped = binned.groupby("Quantity_Bin", observed=True, as_index=False)["Profit"].sum()
    fig = px.bar(grouped, x="Quantity_Bin", y="Profit", color_discrete_sequence=[CHART_PALETTE[1]])
    fig.update_layout(xaxis_title="Order Quantity (binned)", yaxis_title="Total Realized Profit")
    return _dark_layout(fig)


def _s7_correlation_heatmap(df):
    cols = ["Sales", "Discount", "Shipping_Cost", "Quantity", "Profit"]
    corr = df[cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    return _dark_layout(fig)


def _s8_actual_vs_predicted(ctx):
    y_test, preds = ctx["y_test"], ctx["preds"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y_test, y=preds, mode="markers",
                              marker=dict(color=CHART_PALETTE[0], opacity=0.65), name="Test Orders"))
    lo, hi = float(min(y_test.min(), preds.min())), float(max(y_test.max(), preds.max()))
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                              line=dict(color=CHART_PALETTE[3], dash="dash"), name="Identity Line"))
    fig.update_layout(xaxis_title="Actual Profit ($)", yaxis_title="Predicted Profit ($)")
    return _dark_layout(fig)


def _s9_residuals(ctx):
    residuals = ctx["y_test"].values - ctx["preds"]
    fig = px.histogram(residuals, nbins=30, color_discrete_sequence=[CHART_PALETTE[2]])
    fig.add_vline(x=0, line_dash="dash", line_color=CHART_PALETTE[3])
    fig.update_layout(xaxis_title="Residual (Actual − Predicted)", yaxis_title="Count", showlegend=False)
    return _dark_layout(fig)


def _horizontal_feature_importance(ctx, top_n=10):
    names = np.array(ctx["feature_names"])
    importances = np.array(ctx["importances"])
    order = np.argsort(importances)[-top_n:]
    fig = go.Figure(go.Bar(
        x=importances[order], y=names[order], orientation="h",
        marker_color=CHART_PALETTE[0],
    ))
    fig.update_layout(xaxis_title="Relative Importance", yaxis_title="Feature")
    return _dark_layout(fig, height=460)


# ---------------------------------------------------------------------------
# CHURN chart builders
# ---------------------------------------------------------------------------

def _churn_label(series):
    return series.map({1: "Churned", 0: "Retained"}).fillna("Retained")


def _c1_churn_donut(df):
    counts = _churn_label(df["Churned"]).value_counts().reset_index()
    counts.columns = ["Status", "Customers"]
    fig = px.pie(counts, names="Status", values="Customers", hole=0.55,
                 color_discrete_sequence=[CHART_PALETTE[1], CHART_PALETTE[3]])
    return _dark_layout(fig)


def _c2_churn_by_contract(df):
    grouped = (df.groupby("Contract_Type")["Churned"].mean() * 100).reset_index(name="Churn Rate (%)")
    fig = px.bar(grouped, x="Contract_Type", y="Churn Rate (%)", color_discrete_sequence=[CHART_PALETTE[3]])
    return _dark_layout(fig)


def _kde_curve(values, n_points=200):
    try:
        from scipy.stats import gaussian_kde
        values = values.dropna().values
        if len(values) < 2 or np.std(values) == 0:
            raise ValueError("insufficient variance for KDE")
        kde = gaussian_kde(values)
        xs = np.linspace(values.min(), values.max(), n_points)
        return xs, kde(xs)
    except Exception:
        hist, edges = np.histogram(values.dropna(), bins=30, density=True)
        xs = (edges[:-1] + edges[1:]) / 2
        return xs, hist


def _c3_monthly_charges_kde(df):
    fig = go.Figure()
    for label, color in [(1, CHART_PALETTE[3]), (0, CHART_PALETTE[1])]:
        subset = df.loc[df["Churned"] == label, "Monthly_Charges"]
        xs, ys = _kde_curve(subset)
        name = "Churned" if label == 1 else "Retained"
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="tozeroy", name=name,
                                  line=dict(color=color)))
    fig.update_layout(xaxis_title="Monthly Charges ($)", yaxis_title="Density")
    return _dark_layout(fig)


def _c4_tenure_histogram(df):
    fig = px.histogram(df, x="Tenure_Months", color=_churn_label(df["Churned"]), barmode="overlay",
                        opacity=0.65, color_discrete_sequence=[CHART_PALETTE[1], CHART_PALETTE[3]])
    fig.update_layout(legend_title_text="Status")
    return _dark_layout(fig)


def _c5_support_tickets_vs_churn(df):
    grouped = (df.groupby("Support_Tickets")["Churned"].mean() * 100).reset_index(name="Churn Rate (%)")
    fig = px.line(grouped, x="Support_Tickets", y="Churn Rate (%)", markers=True,
                  color_discrete_sequence=[CHART_PALETTE[4]])
    return _dark_layout(fig)


def _c6_addon_adoption(df):
    combo = df.copy()
    combo["Add-On Bundle"] = np.where(
        (combo["Tech_Support"].astype(str) == "Yes") & (combo["Online_Security"].astype(str) == "Yes"),
        "Both Add-Ons",
        np.where(
            (combo["Tech_Support"].astype(str) == "Yes") | (combo["Online_Security"].astype(str) == "Yes"),
            "One Add-On", "No Add-Ons"
        )
    )
    grouped = (combo.groupby("Add-On Bundle")["Churned"].mean() * 100).reset_index(name="Churn Rate (%)")
    fig = px.bar(grouped, x="Add-On Bundle", y="Churn Rate (%)", color_discrete_sequence=[CHART_PALETTE[0]])
    return _dark_layout(fig)


def _c7_payment_method(df):
    grouped = (df.groupby("Payment_Method")["Churned"].mean() * 100).reset_index(name="Churn Rate (%)")
    fig = px.bar(grouped.sort_values("Churn Rate (%)", ascending=False), x="Payment_Method", y="Churn Rate (%)",
                 color_discrete_sequence=[CHART_PALETTE[5]])
    fig.update_xaxes(tickangle=-20)
    return _dark_layout(fig)


def _c8_correlation_heatmap(df):
    cols = ["Tenure_Months", "Monthly_Charges", "Total_Charges", "Support_Tickets",
            "Complaints", "Satisfaction_Score", "NPS", "Churned"]
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    return _dark_layout(fig, height=480)


def _c9_roc_curves(multi_ctx):
    fig = go.Figure()
    for i, (name, data) in enumerate(multi_ctx["roc_data"].items()):
        color = CHART_PALETTE[i % len(CHART_PALETTE)]
        fig.add_trace(go.Scatter(
            x=data["fpr"], y=data["tpr"], mode="lines",
            name=f"{name} (AUC={data['auc']:.3f})", line=dict(color=color)
        ))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                              line=dict(color="gray", dash="dash"), name="Random Chance"))
    fig.update_layout(xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    return _dark_layout(fig, height=460)


def _c10_confusion_matrices(ctx):
    y_test, probs = ctx["y_test"], ctx["probs"]
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Default Threshold (0.50)", "Tuned Threshold (0.38)"))
    for col, thresh in enumerate([0.50, 0.38], start=1):
        preds = (probs >= thresh).astype(int)
        cm = confusion_matrix(y_test, preds)
        fig.add_trace(go.Heatmap(
            z=cm, x=["Pred: Retained", "Pred: Churned"], y=["Actual: Retained", "Actual: Churned"],
            text=cm, texttemplate="%{text}", colorscale="Blues", showscale=(col == 2)
        ), row=1, col=col)
    return _dark_layout(fig, height=420)


# ---------------------------------------------------------------------------
# HR_ATTRITION chart builders
# ---------------------------------------------------------------------------

def _attr_label(series):
    return series.map({1: "Attrited", 0: "Retained"}).fillna("Retained")


def _h1_attrition_donut(df):
    counts = _attr_label(df["Attrition"]).value_counts().reset_index()
    counts.columns = ["Status", "Employees"]
    fig = px.pie(counts, names="Status", values="Employees", hole=0.55,
                 color_discrete_sequence=[CHART_PALETTE[1], CHART_PALETTE[3]])
    return _dark_layout(fig)


def _h2_overtime_attrition(df):
    grouped = (df.groupby("Overtime")["Attrition"].mean() * 100).reset_index(name="Attrition Rate (%)")
    fig = px.bar(grouped, x="Overtime", y="Attrition Rate (%)", color_discrete_sequence=[CHART_PALETTE[3]])
    return _dark_layout(fig)


def _h3_income_by_attrition(df):
    plot_df = df.copy()
    plot_df["Attrition"] = _attr_label(plot_df["Attrition"])
    fig = px.box(plot_df, x="Attrition", y="Monthly_Income", color="Attrition",
                 color_discrete_sequence=[CHART_PALETTE[1], CHART_PALETTE[3]])
    fig.update_layout(showlegend=False)
    return _dark_layout(fig)


def _h4_dept_role_attrition(df):
    grouped = (df.groupby(["Department", "Job_Role"])["Attrition"].mean() * 100).reset_index(name="Attrition Rate (%)")
    fig = px.bar(grouped, x="Job_Role", y="Attrition Rate (%)", color="Department",
                 color_discrete_sequence=CHART_PALETTE, barmode="group")
    fig.update_xaxes(tickangle=-35)
    return _dark_layout(fig, height=460)


def _h5_role_vs_tenure(df):
    plot_df = df.copy()
    plot_df["Attrition"] = _attr_label(plot_df["Attrition"])
    fig = px.scatter(plot_df, x="Years_At_Company", y="Years_In_Current_Role", color="Attrition",
                      color_discrete_sequence=[CHART_PALETTE[1], CHART_PALETTE[3]], opacity=0.7)
    return _dark_layout(fig)


def _h6_satisfaction_matrix(df):
    pivot = df.pivot_table(index="Work_Life_Balance", columns="Job_Satisfaction",
                            values="Attrition", aggfunc="mean") * 100
    fig = px.imshow(pivot.round(1), text_auto=True, color_continuous_scale="Oranges",
                     labels=dict(color="Attrition Rate (%)"))
    return _dark_layout(fig)


def _h7_commute_kde(df):
    fig = go.Figure()
    for label, color in [(1, CHART_PALETTE[3]), (0, CHART_PALETTE[1])]:
        subset = df.loc[df["Attrition"] == label, "Distance_From_Home"]
        xs, ys = _kde_curve(subset)
        name = "Attrited" if label == 1 else "Retained"
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="tozeroy", name=name,
                                  line=dict(color=color)))
    fig.update_layout(xaxis_title="Distance From Home (miles)", yaxis_title="Density")
    return _dark_layout(fig)


def _h8_workmode_attrition(df):
    grouped = (df.groupby("Work_Mode")["Attrition"].mean() * 100).reset_index(name="Attrition Rate (%)")
    fig = px.bar(grouped, x="Work_Mode", y="Attrition Rate (%)", color_discrete_sequence=[CHART_PALETTE[0]])
    return _dark_layout(fig)


def _h9_missing_value_strategies(df):
    results = run_missing_value_strategies(df)
    rows = [{"Strategy": v["strategy"], "F1 Score": v["f1_score"], "Recall": v["recall"]} for v in results.values()]
    melted = pd.DataFrame(rows).melt(id_vars="Strategy", value_vars=["F1 Score", "Recall"],
                                      var_name="Metric", value_name="Score")
    fig = px.bar(melted, x="Strategy", y="Score", color="Metric", barmode="group",
                 color_discrete_sequence=[CHART_PALETTE[0], CHART_PALETTE[1]])
    fig.update_xaxes(tickangle=-15)
    return _dark_layout(fig, height=460)


def _h10_equity_audit(ctx, df):
    X_test = ctx["X_test"]
    y_test = ctx["y_test"]
    preds = ctx["preds"]
    if "Gender" not in X_test.columns:
        fig = go.Figure()
        fig.add_annotation(text="Gender column unavailable for subgroup audit", showarrow=False)
        return _dark_layout(fig)

    audit_rows = []
    for gender in X_test["Gender"].unique():
        mask = (X_test["Gender"] == gender).values
        if mask.sum() == 0:
            continue
        recall = recall_score(y_test[mask], preds[mask], zero_division=0)
        audit_rows.append({"Gender": gender, "Recall": recall, "Group Size": int(mask.sum())})
    audit_df = pd.DataFrame(audit_rows)
    fig = px.bar(audit_df, x="Gender", y="Recall", color="Gender", text="Group Size",
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(texttemplate="n=%{text}", textposition="outside")
    fig.update_layout(yaxis_range=[0, 1.05], showlegend=False)
    return _dark_layout(fig)


def _h11_cv_stability(cv_scores):
    fig = go.Figure()
    fig.add_trace(go.Box(y=cv_scores, name="Random Forest", marker_color=CHART_PALETTE[0], boxmean=True))
    fig.add_trace(go.Scatter(
        x=["Random Forest"] * len(cv_scores), y=cv_scores, mode="markers",
        marker=dict(color=CHART_PALETTE[2], size=9), name="Fold Score"
    ))
    fig.update_layout(yaxis_title="F1 Score")
    return _dark_layout(fig)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def build_figure(
    chart_id: str,
    project_option: str,
    df: "pd.DataFrame",
    primary_ctx: Optional[Dict[str, Any]] = None,
    multi_ctx: Optional[Dict[str, Any]] = None,
    cv_scores: Optional[List[float]] = None,
):
    """Returns the Plotly figure for the given chart id, or None if it cannot be built."""
    try:
        if project_option == "SALES":
            builders = {
                "CHART_S1": lambda: _s1_profit_histogram(df),
                "CHART_S2": lambda: _s2_discount_vs_profit(df),
                "CHART_S3": lambda: _s3_profit_by_category(df),
                "CHART_S4": lambda: _s4_shipping_ratio_by_mode(df),
                "CHART_S5": lambda: _s5_regional_sales_profit(df),
                "CHART_S6": lambda: _s6_quantity_binned_margin(df),
                "CHART_S7": lambda: _s7_correlation_heatmap(df),
                "CHART_S8": lambda: _s8_actual_vs_predicted(primary_ctx),
                "CHART_S9": lambda: _s9_residuals(primary_ctx),
                "CHART_S10": lambda: _horizontal_feature_importance(primary_ctx),
            }
        elif project_option == "CHURN":
            builders = {
                "CHART_C1": lambda: _c1_churn_donut(df),
                "CHART_C2": lambda: _c2_churn_by_contract(df),
                "CHART_C3": lambda: _c3_monthly_charges_kde(df),
                "CHART_C4": lambda: _c4_tenure_histogram(df),
                "CHART_C5": lambda: _c5_support_tickets_vs_churn(df),
                "CHART_C6": lambda: _c6_addon_adoption(df),
                "CHART_C7": lambda: _c7_payment_method(df),
                "CHART_C8": lambda: _c8_correlation_heatmap(df),
                "CHART_C9": lambda: _c9_roc_curves(multi_ctx),
                "CHART_C10": lambda: _c10_confusion_matrices(primary_ctx),
            }
        else:  # HR_ATTRITION
            builders = {
                "CHART_H1": lambda: _h1_attrition_donut(df),
                "CHART_H2": lambda: _h2_overtime_attrition(df),
                "CHART_H3": lambda: _h3_income_by_attrition(df),
                "CHART_H4": lambda: _h4_dept_role_attrition(df),
                "CHART_H5": lambda: _h5_role_vs_tenure(df),
                "CHART_H6": lambda: _h6_satisfaction_matrix(df),
                "CHART_H7": lambda: _h7_commute_kde(df),
                "CHART_H8": lambda: _h8_workmode_attrition(df),
                "CHART_H9": lambda: _h9_missing_value_strategies(df),
                "CHART_H10": lambda: _h10_equity_audit(primary_ctx, df),
                "CHART_H11": lambda: _h11_cv_stability(cv_scores or []),
                "CHART_H12": lambda: _horizontal_feature_importance(primary_ctx),
            }
        builder = builders.get(chart_id)
        return builder() if builder else None
    except Exception:
        return None
