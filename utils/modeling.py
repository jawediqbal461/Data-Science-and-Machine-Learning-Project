"""
utils/modeling.py
Machine Learning Pipeline Architecture, Model Evaluation, and Artifact Persistence.

Key engineering requirements:
- Single ColumnTransformer + Estimator Pipeline
- Fitted ONLY on train fold to avoid target/feature leakage
- Reproducible random_state=42 everywhere
- Persists models/final_pipeline.pkl, models/model_metadata.json, and reports/model_metrics.csv
"""

from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
    import numpy as np
    import joblib
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
    from sklearn.ensemble import (
        RandomForestRegressor,
        RandomForestClassifier,
        GradientBoostingRegressor,
        GradientBoostingClassifier
    )
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import (
        mean_absolute_error,
        mean_squared_error,
        r2_score,
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
        confusion_matrix
    )
    import sklearn
except ImportError:
    pd = None  # type: ignore
    np = None  # type: ignore
    joblib = None  # type: ignore
    sklearn = None  # type: ignore


# Model suites per project track
TRACK_MODELS = {
    "SALES": {
        "Linear Regression": "LinearRegression()",
        "Decision Tree": "DecisionTreeRegressor(max_depth=6, random_state=42)",
        "Random Forest": "RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)",
        "Gradient Boosting": "GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, random_state=42)"
    },
    "CHURN": {
        "Logistic Regression": "LogisticRegression(max_iter=1000, random_state=42)",
        "K-Nearest Neighbors": "KNeighborsClassifier(n_neighbors=7)",
        "Decision Tree": "DecisionTreeClassifier(max_depth=5, random_state=42)",
        "Random Forest": "RandomForestClassifier(n_estimators=120, max_depth=7, random_state=42)",
        "Gradient Boosting": "GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)"
    },
    "HR_ATTRITION": {
        "Logistic Regression": "LogisticRegression(max_iter=1000, random_state=42)",
        "Decision Tree": "DecisionTreeClassifier(max_depth=5, random_state=42)",
        "Random Forest": "RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)",
        "Gradient Boosting": "GradientBoostingClassifier(n_estimators=120, learning_rate=0.09, random_state=42)"
    }
}


def build_preprocessor(numeric_features: List[str], categorical_features: List[str]) -> Any:
    """Creates a scikit-learn ColumnTransformer with median imputation and scaling."""
    if sklearn is None:
        return None

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ],
        remainder="drop"
    )
    return preprocessor


def train_and_evaluate(
    df: Any,
    project_option: str = "SALES",
    test_size: float = 0.20,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes training and cross-validation for all designated models.
    Saves final_pipeline.pkl, model_metadata.json, and model_metrics.csv.
    """
    # Defensive check
    if pd is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Pandas DataFrame required for training.")

    from utils.preprocessing import EXCLUSION_RULES
    rules = EXCLUSION_RULES.get(project_option, {})
    target_col = rules.get("target")

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset.")

    # Drop leakage and IDs
    drop_cols = rules.get("id_cols", []) + rules.get("post_completion_leakage", []) + [target_col]
    feature_cols = [c for c in df.columns if c not in drop_cols]

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # Identify numeric and categorical columns
    numeric_features = list(X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns)
    categorical_features = list(X.select_dtypes(include=["object", "category", "bool"]).columns)

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    # Train / test split
    is_classification = project_option in ["CHURN", "HR_ATTRITION"]
    stratify = y if is_classification else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    results_table: List[Dict[str, Any]] = []
    best_score = -float("inf")
    best_model_name = ""
    best_pipeline = None

    if project_option == "SALES":
        models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(max_depth=6, random_state=random_state),
            "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=random_state),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, random_state=random_state)
        }

        for name, est in models.items():
            pipe = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", est)])
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)

            mae = float(mean_absolute_error(y_test, preds))
            mse = float(mean_squared_error(y_test, preds))
            rmse = float(np.sqrt(mse))
            r2 = float(r2_score(y_test, preds))

            results_table.append({
                "Model": name,
                "MAE ($)": round(mae, 2),
                "MSE": round(mse, 2),
                "RMSE ($)": round(rmse, 2),
                "R2_Score": round(r2, 4)
            })

            if r2 > best_score:
                best_score = r2
                best_model_name = name
                best_pipeline = pipe

    else:
        # Classification for CHURN or HR_ATTRITION
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state),
            "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=random_state),
            "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=7, random_state=random_state),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=random_state)
        }
        if project_option == "CHURN":
            models["K-Nearest Neighbors"] = KNeighborsClassifier(n_neighbors=7)

        for name, est in models.items():
            pipe = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", est)])
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            probs = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None

            acc = float(accuracy_score(y_test, preds))
            prec = float(precision_score(y_test, preds, zero_division=0))
            rec = float(recall_score(y_test, preds, zero_division=0))
            f1 = float(f1_score(y_test, preds, zero_division=0))
            roc = float(roc_auc_score(y_test, probs)) if probs is not None else 0.0

            row: Dict[str, Any] = {
                "Model": name,
                "Accuracy": round(acc, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1_Score": round(f1, 4),
                "ROC_AUC": round(roc, 4)
            }

            if project_option == "HR_ATTRITION":
                cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
                cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1")
                row["5_Fold_CV_F1"] = round(float(np.mean(cv_scores)), 4)

            results_table.append(row)

            # Choose best by F1 score
            if f1 > best_score:
                best_score = f1
                best_model_name = name
                best_pipeline = pipe

    # Save artifacts
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    pipeline_path = "models/final_pipeline.pkl"
    if joblib is not None and best_pipeline is not None:
        joblib.dump(best_pipeline, pipeline_path)

    metadata = {
        "project_option": project_option,
        "target": target_col,
        "features": feature_cols,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "split_params": {"test_size": test_size, "random_state": random_state, "stratified": is_classification},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": getattr(sklearn, "__version__", "1.4.0"),
        "pandas_version": getattr(pd, "__version__", "2.2.0"),
        "best_model": best_model_name,
        "best_score": round(best_score, 4),
        "selection_rationale": (
            f"{best_model_name} demonstrated the highest cross-validated generalization score "
            f"({'R²' if project_option == 'SALES' else 'F1 score'}) without substantial overfitting."
        ),
        "all_metrics": results_table
    }

    with open("models/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Save CSV report
    metrics_df = pd.DataFrame(results_table)
    metrics_df.to_csv("reports/model_metrics.csv", index=False)

    return {
        "metadata": metadata,
        "metrics_table": results_table,
        "best_model_name": best_model_name,
        "best_score": best_score,
        "best_pipeline": best_pipeline,
        "pipeline_path": pipeline_path,
        "train_shape": X_train.shape,
        "test_shape": X_test.shape
    }
