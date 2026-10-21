"""
pages/4_Model_Evaluation.py
Machine Learning Model Comparison, Pipeline Specs, and Metric Tables.

Trains every candidate model for the active track on whatever dataset is
actually loaded (bundled sample or the user's own upload), compares them
on the required metrics, and selects the best one live — rather than
displaying fixed numbers that never change with the data.
"""

import pandas as pd
import streamlit as st
from sklearn.metrics import confusion_matrix

from utils.header import render_header
from utils.model_cache import prepare_dataset, get_model_comparison

st.set_page_config(page_title="Model Evaluation", page_icon="🤖", layout="wide")
render_header()
project_opt = st.session_state.get("project_option", "SALES")

st.title(f"🤖 Machine Learning Model Evaluation: {project_opt}")

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
    st.error(f"Failed to prepare dataset for training: {e}")
    st.stop()

is_classification = project_opt in ("CHURN", "HR_ATTRITION")

with st.spinner(f"Training {('4-5' if is_classification else '4')} candidate models on {len(active_df):,} rows..."):
    try:
        result = get_model_comparison(active_df, project_opt)
    except Exception as e:
        st.error(f"Model training failed on the active dataset: {e}")
        st.stop()

metadata = result["metadata"]
metrics_df = pd.DataFrame(result["metrics_table"])
best_name = result["best_model_name"]

st.markdown(f"### 📊 Held-Out Test Evaluation — trained live on `{len(active_df):,}` active rows ({metadata['train_rows']:,} train / {metadata['test_rows']:,} test)")

sort_col = "R2_Score" if project_opt == "SALES" else "F1_Score"


def _highlight_best(row):
    is_best = row["Model"] == best_name
    return ["background-color: rgba(34,197,94,0.18); font-weight:600" if is_best else "" for _ in row]


display_df = metrics_df.sort_values(sort_col, ascending=False).reset_index(drop=True)
st.dataframe(display_df.style.apply(_highlight_best, axis=1), use_container_width=True)

st.info(
    f"💡 **Selection Rationale**: **{best_name}** was selected as the production pipeline — "
    + metadata["selection_rationale"]
)

st.markdown("---")
st.markdown("### 📈 Required Model Visualizations")

primary_ctx_cols = st.columns(2)

if project_opt == "SALES":
    from utils.model_cache import get_primary_model_context
    import plotly.express as px

    ctx = get_primary_model_context(active_df, project_opt)
    with primary_ctx_cols[0]:
        fig = px.scatter(
            x=ctx["y_test"], y=ctx["preds"],
            labels={"x": "Actual Profit ($)", "y": "Predicted Profit ($)"},
            title="Actual vs. Predicted Profit (Best Pipeline)", opacity=0.6,
        )
        fig.add_shape(type="line", x0=min(ctx["y_test"]), y0=min(ctx["y_test"]),
                      x1=max(ctx["y_test"]), y1=max(ctx["y_test"]), line=dict(color="red", dash="dash"))
        st.plotly_chart(fig, use_container_width=True)
    with primary_ctx_cols[1]:
        residuals = ctx["y_test"] - ctx["preds"]
        fig2 = px.histogram(residuals, nbins=40, title="Residual Distribution", labels={"value": "Residual ($)"})
        st.plotly_chart(fig2, use_container_width=True)

    fi_df = pd.DataFrame({"Feature": ctx["feature_names"], "Importance": ctx["importances"]}).sort_values(
        "Importance", ascending=False
    ).head(12)
    fig3 = px.bar(fi_df, x="Importance", y="Feature", orientation="h", title="Feature Importance (Top 12)")
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)

else:
    from utils.model_cache import get_primary_model_context, get_classifier_suite_context
    import plotly.express as px
    import plotly.graph_objects as go

    ctx = get_primary_model_context(active_df, project_opt)
    cm = confusion_matrix(ctx["y_test"], ctx["preds"])

    with primary_ctx_cols[0]:
        fig_cm = px.imshow(
            cm, text_auto=True, color_continuous_scale="Blues",
            labels=dict(x="Predicted", y="Actual"),
            x=["Retained/No", "Churned/Yes"], y=["Retained/No", "Churned/Yes"],
            title="Confusion Matrix (Best Single Pipeline)",
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    with primary_ctx_cols[1]:
        try:
            multi_ctx = get_classifier_suite_context(active_df, project_opt)
            fig_roc = go.Figure()
            for name, d in multi_ctx["roc_data"].items():
                fig_roc.add_trace(go.Scatter(x=d["fpr"], y=d["tpr"], mode="lines", name=f"{name} (AUC={d['auc']:.3f})"))
            fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dash", color="gray"), name="Chance"))
            fig_roc.update_layout(title="ROC Curves — All Candidate Models", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
            st.plotly_chart(fig_roc, use_container_width=True)
        except Exception as e:
            st.warning(f"ROC comparison unavailable: {e}")

    if ctx.get("importances") is not None:
        fi_df = pd.DataFrame({"Feature": ctx["feature_names"], "Importance": ctx["importances"]}).sort_values(
            "Importance", ascending=False
        ).head(12)
        fig3 = px.bar(fi_df, x="Importance", y="Feature", orientation="h", title="Feature Importance (Top 12)")
        fig3.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

with st.expander("🔧 Model Comparison Chart"):
    import plotly.express as px
    y_metric = "R2_Score" if project_opt == "SALES" else "F1_Score"
    fig_cmp = px.bar(display_df, x="Model", y=y_metric, title=f"Model Comparison — {y_metric}", text=y_metric)
    st.plotly_chart(fig_cmp, use_container_width=True)

st.caption(
    "Every model above and its metrics are trained fresh on the dataset currently active in the "
    "top navigation bar — switch tracks or upload a new file and this page retrains automatically."
)
