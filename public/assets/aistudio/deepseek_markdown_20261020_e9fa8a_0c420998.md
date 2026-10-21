# MASTER PROMPT v2 — Data Science Streamlit Capstone (Multi-Source Data Ingestion)

## 0) Config — fill before sending

PROJECT_OPTION      : <SALES | CHURN | HR_ATTRITION>
PROJECT_TITLE       : (Data Science and Machine Learning Assignment Project | 1: Sales Analytics and Profit Prediction | 2: Customer Churn Prediction | 3: HR Analytics and Employee Attrition)
STUDENT_NAME        : Jawed Iqbal
GROUP_MEMBER        : <Nil>
COURSE_NAME         : Data Science and Machine Learning
DATASET_PATH        : <path to real CSV/Excel OR "NOT_PROVIDED_YET">
GITHUB_REPO         : <repo name OR "NOT_CREATED_YET">
DEPLOYMENT_URL      : <after deploy OR "PENDING">
WORKSPACE_PATH      : <local folder>
DEADLINE            : 22 October 2026
TEAM_SIZE           : 2
BONUS_TARGETS       : <comma list — e.g. "webhook_ingest, docker, pytests, plotly">
                      If unsure, use: "webhook_ingest, plotly, pytests"

---

## 1) Role

Act as my **senior Python data-science engineer + ML mentor + Streamlit developer + QA + deployment guide**. Build a submission-ready project for the selected PROJECT_OPTION. Teach every major decision in beginner-friendly language so I can defend it in a viva.

**Non-negotiables:** never invent the final dataset, results, screenshots, or metrics. Never claim deployment happened until I confirm. Never use synthetic data as "real findings". If the real dataset is missing, build a clearly labelled `MISSING_DATASET` state and stop analysis until the file arrives.

---

## 2) CRITICAL — Data Ingestion Architecture (read before anything else)

The app must support **multiple data-ingestion modes via a clean adapter pattern**. This is the #1 architectural requirement.

### 2.1 Abstract interface — `utils/data_source.py`

Define an abstract `DataSource` with two methods:
- `load() -> tuple[pd.DataFrame, DataSourceMeta]`
- `describe() -> str` (for the UI to display "Currently using: ...")

`DataSourceMeta` = dataclass with: `source_type`, `source_label`, `loaded_at` (UTC ISO), `row_count`, `column_count`, `sha256` of the DataFrame's `to_csv()` for change-detection, `warnings: list[str]`.

### 2.2 Concrete adapters — implement ALL of these unless marked optional

| Adapter | Purpose | Required? |
|---|---|---|
| `BundledCSVSource` | Ships with `data/dataset.csv` — **default on cold start** | ✅ Required |
| `UploadedFileSource` | `st.file_uploader` — CSV/XLSX, per-session only | ✅ Required |
| `WebhookPushSource` | Reads latest file from `data/incoming/` written by a FastAPI sidecar; HMAC-verified | ⭐ Bonus |
| `DatabaseReadOnlySource` | Postgres/Supabase read-only via `st.secrets` (SQL SELECT only, no writes) | ⭐ Optional |
| `RestAPIPullSource` | Pulls JSON/CSV from an endpoint with API key in `st.secrets` | ⭐ Optional |

Only implement the bonus/optional adapters if `BONUS_TARGETS` includes them. If skipped, still define the abstract interface so the architecture is visible.

### 2.3 Webhook sidecar — `webhook_server.py` (bonus mode)

Standalone FastAPI app:
- `POST /webhook/ingest` — header `X-Signature` = HMAC-SHA256(body, `WEBHOOK_SECRET` from env). Reject unsigned. Save to `data/incoming/<uuid>.csv`. Return `{id, received_at, row_count, sha256}`.
- `GET /webhook/health` — for uptime check.
- Fully independent of Streamlit; runs on port 8000. Streamlit app polls `data/incoming/` when the user picks "Webhook" source.
- Document `curl` example + a `send_webhook_demo.py` script for the viva demo.

### 2.4 Session safety

Store in `st.session_state` **only**:
- `active_source_key` (string)
- `active_data_hash` (sha256)
- `active_df` **only** if source is `UploadedFileSource`

Bundled data loads from disk via `@st.cache_data`. Uploads never touch disk. This makes multi-user deployment safe (each browser session sees only its own upload).

### 2.5 Persistence reality — Streamlit Cloud

Add a prominent `st.info` on the data-source panel:

> "Streamlit Community Cloud has an ephemeral filesystem. Uploaded files and webhook-received files **do not survive a restart**. The bundled demo dataset is always available. For real persistence, connect Supabase/S3 (documented in README, not implemented)."

Document this in README → "Deployment constraints" section.

### 2.6 Validation gate — `utils/validation.py`

**Every** DataFrame from **any** adapter must pass `validate_dataset(df, required_columns, target_column) -> ValidationReport` before analysis or training. On failure: show `st.error` with a schema table (Required / Present / Missing), offer a **column-mapping UI** (`st.selectbox` per missing concept → existing column) — only allow mappings where meaning is unambiguous. Never silently rename. If the target column is missing entirely, disable ML training.

---

## 3) Project directory tree
project_name/
├── app.py # entry, sidebar source selector, health check
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml # theme + server settings
├── data/
│ ├── README.md # dataset provenance + how to obtain
│ ├── dataset.csv # bundled real dataset (or .gitkeep + instructions)
│ └── incoming/.gitkeep # webhook drop zone (bonus)
├── models/
│ ├── final_pipeline.pkl # generated, not committed initially
│ └── model_metadata.json
├── reports/
│ ├── model_metrics.csv
│ ├── business_recommendations.md
│ └── data_quality_report.md
├── pages/ # all mandatory pages for the selected project
│ ├── 1_Home.py
│ ├── 2_Data_Explorer.py
│ ├── ... # per project (see §6)
├── utils/
│ ├── data_source.py # adapters (§2)
│ ├── data_loader.py # thin wrapper around active source
│ ├── validation.py # schema gate
│ ├── preprocessing.py # cleaning + feature engineering
│ ├── feature_engineering.py
│ ├── charts.py # reusable chart builders
│ ├── modeling.py # training + evaluation
│ ├── prediction.py # load pipeline, run inference
│ ├── recommendations.py # Finding/Evidence/Recommendation/Expected Outcome
│ └── persistence.py # optional Supabase/S3 helpers (documented only if not in scope)
├── webhook_server.py # bonus: FastAPI sidecar
├── send_webhook_demo.py # bonus: curl-equivalent demo for viva
├── notebooks/
│ └── project_analysis.ipynb
├── tests/
│ ├── test_validation.py
│ ├── test_adapters.py
│ ├── test_preprocessing.py
│ └── test_prediction.py
└── assets/screenshots/ # real screenshots after running


Every created file must have a purpose. No empty placeholders.

---

## 4) Build phases (in this exact order — verify each before moving on)

**Phase 1 — Workspace + dataset discovery.** Inspect existing files. If real dataset present: report shape, dtypes, missing %, dupes, date range, target distribution, and a **column mapping table** vs the assignment's expected schema. If absent: create a `MISSING_DATASET` state + working UI skeleton. **Do not proceed to modeling without real data.**

**Phase 2 — Data source architecture.** Implement all `DataSource` adapters per §2. Write `tests/test_adapters.py` covering: bundled loads, upload with wrong columns triggers validation error, upload with correct columns passes, webhook file with bad HMAC rejected. Gate to continue: bundled + upload adapters fully tested.

**Phase 3 — Cleaning + feature engineering.** Implement in `preprocessing.py` / `feature_engineering.py`. Follow the assignment's cleaning rules exactly for the selected project. Guard every division by zero. Document each engineering feature: formula + business meaning + leakage check.

**Phase 4 — EDA.** Complete every mandatory question + every mandatory visualization for the selected project (see §6). Every chart: title, axis labels, readable size. Add a 1-line caption stating what it shows (no causal claims).

**Phase 5 — Modeling.** `ColumnTransformer` + estimator in **one** `Pipeline`, saved via `joblib.dump`. Fit only on train. Stratified split for classification. Train all mandatory models for the selected project. Compute every required metric on held-out test. Save `reports/model_metrics.csv` and `models/model_metadata.json` with: target, feature names, split params, timestamp, versions of sklearn/pandas, chosen model + rationale, and per-model metrics. Save the **best** complete pipeline.

**Phase 6 — Streamlit pages.** Build every mandatory page (§6). Reuse `utils/charts.py` and `utils/data_loader.py` — no duplicated plotting code. Sidebar shows: active source (with `describe()`), target column, and "Retrain" button (writes new artifacts — disabled in prod). Every page must degrade gracefully when data is missing or empty.

**Phase 7 — Prediction + explainability.** Same preprocessing as training (pipeline handles it). Validate form inputs against training ranges. Show the exact output fields for the selected project. Explain limits in plain language.

**Phase 8 — Recommendations.** Minimum count per selected project. Strict Finding / Evidence / Recommendation / Expected Outcome. Number every Evidence with the exact table/plot/metric that supports it. Label unsupported ideas "hypothesis to test".

**Phase 9 — Notebook + reports.** `notebooks/project_analysis.ipynb` mirrors the app's logic — no contradictions. `reports/data_quality_report.md`, `reports/model_metrics.csv`, `reports/business_recommendations.md`.

**Phase 10 — QA.** Run: `python -m compileall .`, `pytest -q`, `streamlit run app.py`. Manually test: no-file state, wrong-schema upload, empty filters, missing model artifact, invalid form values, threshold slider (CHURN), subgroup audit (HR). Produce a **Passed / Failed / Not-yet-verified** report.

**Phase 11 — GitHub + Streamlit Cloud.** Provide exact commands + step-by-step dashboard clicks. Do **not** claim deployment. Ask me to confirm.

---

## 5) Project-specific requirements (implement ONLY for PROJECT_OPTION)

### If SALES
- Target: `Profit`. Exclude `Order_ID`, `Customer_ID`, `Customer_Name`. Also exclude `Customer_Rating`, `Returned`, `Total_Sale` for pre-completion prediction (explain timing assumption).
- Models: Linear Regression, Decision Tree, Random Forest (+ optional Gradient Boosting).
- Metrics: MAE, MSE, RMSE, R².
- Plots: actual vs predicted, residual distribution, model comparison, feature importance.
- ≥5 engineered features, ≥10 EDA charts, ≥5 recommendations.
- Pages: Home, Dataset Explorer, Sales Dashboard, Product & Regional Analysis, Customer & Delivery Analysis, Model Evaluation, Profit Prediction.
- Profit categories: Loss / Low / Medium / High — thresholds configurable in `utils/config.py` with documented rationale.
- Negative profit → prominent red warning in prediction page.

### If CHURN
- Target: `Churned` (Yes→1, No→0; reject unmapped values).
- Exclude `Customer_ID`, `Customer_Name`, `Signup_Date`. Check for other leakage.
- Models: Logistic Regression, KNN, Decision Tree, Random Forest (+ optional Gradient Boosting).
- Metrics: Accuracy, Precision, Recall, F1, ROC-AUC.
- Plots: churn distribution, by contract/subscription/payment/auto-pay/segment/region, monthly charges/tenure/satisfaction/complaints/support tickets/late payments/NPS vs churn, correlation heatmap, confusion matrix, ROC, PR, feature importance.
- **Threshold Analysis page:** slider 0–1, recompute precision/recall/F1/FP/FN/num-high-risk at chosen threshold — no retrain.
- **Retention Dashboard:** high-risk count, revenue-at-risk (explicit formula, no double counting), by region/segment, downloadable high-risk list (anonymised).
- Risk bands: Low/Medium/High/Critical — configurable.
- ≥5 engineered features, ≥10 EDA charts, ≥5 recommendations.

### If HR_ATTRITION
- Target: `Attrition` (Yes→1, No→0).
- Exclude `Employee_ID`, `Employee_Name`, `Hire_Date` from model features. Keep IDs for **display only** (anonymised).
- **Mandatory ethical banner on every page + prediction page:**
  > "This prediction is intended for workforce-level analysis and voluntary retention support. It must not be used as the sole basis for termination, promotion, salary, disciplinary, or hiring decisions."
- Missing-value comparison: **all four** strategies (row-drop, mean, median, most-frequent). Pipeline default: median (numeric) + most-frequent (categorical). Show a comparison table with model F1/recall per strategy (fit on train only).
- Models: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting (+ optional SVM).
- Metrics: Accuracy, Precision, Recall, F1, ROC-AUC, **plus** 5-fold CV score.
- Preprocessing Laboratory page: numerical cols, categorical cols, missing-strategy, processed feature count, train/test shapes.
- **Responsible ML Review page:** by gender/age-group/department/employment-type/work-mode — group size, actual attrition rate, predicted rate, recall, FPR. Warn on small groups (n < 30).
- ≥8 engineered features, ≥12 EDA charts, ≥7 recommendations.

---

## 6) Streamlit pages (per option)

- **SALES:** Home, Dataset Explorer, Sales Dashboard, Product & Regional, Customer & Delivery, Model Evaluation, Profit Prediction (7).
- **CHURN:** Home, Customer Explorer, Churn Dashboard, Churn Analysis, Model Comparison, Threshold Analysis, Churn Prediction, Retention Dashboard (8).
- **HR:** Home, Data Quality, Executive Dashboard, Demographics, Compensation, Engagement, Attrition Analysis, Preprocessing Lab, Model Comparison, Risk Assessment, Responsible ML Review (11).

Sidebar (all pages): active source selector + `describe()` + active target column + "Reload bundled data" button.

---

## 7) Common technical rules

- **Caching:** `@st.cache_data` for data loads (keyed on file path + hash), `@st.cache_resource` for model loads. Never cache mutable session state.
- **Model save:** full `Pipeline` via `joblib.dump(pipeline, "models/final_pipeline.pkl")`. Ship `model_metadata.json` alongside. If artifact missing, show a "Run `python -m utils.modeling train`" message — never fake a prediction.
- **Reproducibility:** `random_state=42` everywhere, document split ratio, log `sklearn.__version__` and `pandas.__version__` in metadata.
- **Leakage:** fit preprocessing only on train. Save the **entire** fitted pipeline so inference uses identical transforms.
- **Privacy:** never use names/IDs as features. HR high-risk table = anon IDs only. Downloads exclude personal columns.
- **Robustness:** wrap every external call. `st.error` + actionable next step. No raw tracebacks to non-admin users.
- **requirements.txt:** only what's imported. Baseline: `streamlit, pandas, numpy, seaborn, matplotlib, scikit-learn, joblib`. Add `openpyxl` if XLSX, `fastapi, uvicorn, python-multipart` if webhook, `plotly` if interactive charts, `pytest` if tests. **No pinning** until you've verified compatibility locally.
- **.gitignore:** `.venv/`, `__pycache__/`, `.pytest_cache/`, `*.pyc`, `.streamlit/secrets.toml`, `data/incoming/*`, `models/*.pkl` (optional — commit only if < 20 MB), `.DS_Store`, `.idea/`, `.vscode/`.
- **Secrets:** `WEBHOOK_SECRET`, DB creds, API keys → `.streamlit/secrets.toml` locally / Streamlit Cloud dashboard in prod. Never in code.

---

## 8) Non-functional — reporting & presentation

- **README** must include: title, business problem, objectives, dataset source + access, tech stack, cleaning decisions, feature-engineering catalogue, EDA summary with chart list, models + metric table + best-model rationale, app page map, ≥5 (or ≥7 HR) recommendations, local run commands, training command, Streamlit Cloud deployment steps, screenshots checklist (capture-from-running-app only), known limitations.
- **Presentation outline:** 5–7 min, split roles between both members. Include: business problem (30s) → dataset (30s) → cleaning (60s) → 2–3 key visuals (90s) → models + best (90s) → live demo (90s) → recommendations (30s). Provide a slide-by-slide plan with speaker names.
- **Viva notes:** one page per major file explaining purpose; one paragraph per model explaining when to prefer it; one line per metric explaining what it measures.

---

## 9) Final response format

End with:

- **Implemented** — files + pages actually created.
- **Data source modes** — which adapters are live (bundled / upload / webhook / db / api), each with a one-line description of its UI entry point.
- **Dataset status** — real path + schema, or `MISSING_DATASET` with exact next step.
- **Cleaning + features** — decisions, counts, leakage exclusions.
- **EDA** — completed charts, blocked charts + reason.
- **Model results** — real metric table, best model + why. `(Not run — no data)` if blocked.
- **Tests** — exact commands + results.
- **Deployment** — steps completed vs still requiring me.
- **Submission checklist** — Complete / Pending / Blocked per deliverable.
- **Limitations** — data, statistical, technical, fairness.
- **Run locally** — Windows PowerShell + macOS/Linux commands.
- **Explain in viva** — 5 bullets per major file/model/metric.

**Start now.** Do not ask me to repeat information already here. If the real dataset is missing, build the full scaffold + adapters + UI with a `MISSING_DATASET` banner and keep every analysis path gated behind validation. Do not stop at a plan — implement, run, debug, verify.
