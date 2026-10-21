# Data Science & Machine Learning Capstone Platform
## Multi-Source Data Ingestion & Predictive Analytics System

**Student:** Jawed Iqbal  
**Group Member:** Nil (Individual Submission)  
**Course:** Data Science and Machine Learning  
**Target Deadline:** 22 October 2026  
**Bonus Targets Implemented:** Webhook Ingestion (`FastAPI` + HMAC-SHA256 sidecar), Plotly Interactive Charts, Pytest/Unittest Suite  

---

## 1. Project Title & Business Problem

### Selected Tracks
1. **Sales Analytics and Profit Prediction (Track 1)**: Forecast transaction profitability, detect destructive discount erosion, optimize delivery cost-to-serve, and alert operations to negative-margin orders prior to order fulfillment.
2. **Customer Churn Prediction (Track 2)**: Identify subscriber flight risk, compute friction indices from support interactions, provide dynamic probability threshold tuning ($\tau = 0.38$), and quantify revenue-at-risk.
3. **HR Analytics and Employee Attrition (Track 3)**: Workforce voluntary retention analysis, missing-value strategy evaluation, subgroup demographic parity audits, and strict ethical governance barriers.

---

## 2. Architecture: Multi-Source Data Ingestion (Adapter Pattern)

The core architectural innovation is the decoupled `DataSource` abstraction defined in `utils/data_source.py`:

```
           ┌───────────────────────┐
           │ DataSource (Abstract) │
           │ - load() -> (df, meta)│
           │ - describe() -> str   │
           └───────────┬───────────┘
                       │
       ┌───────────────┼───────────────┬───────────────────┐
       ▼               ▼               ▼                   ▼
┌──────────────┐┌──────────────┐┌───────────────┐ ┌───────────────────┐
│BundledCSV    ││UploadedFile  ││WebhookPush    │ │DatabaseReadOnly   │
│Source        ││Source        ││Source         │ │Source (SQL SELECT)│
│(Local Disk)  ││(In-Memory)   ││(HMAC-SHA256)  │ │& RestAPIPullSource│
└──────────────┘└──────────────┘└───────────────┘ └───────────────────┘
```

### Ingestion Adapters
1. **`BundledCSVSource`**: Default cold-start adapter reading `data/dataset.csv`. Computes SHA-256 for integrity auditing. Cached with `@st.cache_data`.
2. **`UploadedFileSource`**: In-memory session upload via `st.file_uploader`. Bytes never touch disk, guaranteeing multi-tenant safety.
3. **`WebhookPushSource`**: Polling adapter reading HMAC-verified streaming CSV drops from `data/incoming/` produced by the FastAPI sidecar (`webhook_server.py`).
4. **`DatabaseReadOnlySource`**: Parameterized SQL query reader connecting to Postgres/Supabase via credentials in `.streamlit/secrets.toml`.
5. **`RestAPIPullSource`**: Streaming ingest polling external HTTPS REST endpoints with Bearer authentication.

---

## 3. Schema Gate & Data Quality Validation

Before any analysis or modeling, all data passes through `utils/validation.py`:
- Checks required predictor columns and prediction target.
- If target column is missing, **ML training is immediately disabled** to prevent invalid execution.
- If columns differ in nomenclature, a **Column-Mapping UI** enables explicit mapping. Silent column renaming is strictly prohibited.
- Generates a structured `ValidationReport` with column status table, missing percentages, and duplicate counts.

---

## 4. Feature Engineering Catalogue

Every engineered feature satisfies: **Formula + Business Domain Meaning + Leakage-Safe Verification + Division-by-Zero Guard**.

### Sales Analytics (≥ 5 Features)
1. `Discount_Per_Quantity` = $Discount / (Quantity + 10^{-6})$: Effective promotional intensity per unit. Pre-checkout attribute (Leakage Safe).
2. `Shipping_Cost_Ratio` = $Shipping\_Cost / (Sales + 10^{-6})$: Logistics burden against gross revenue. Pre-fulfillment (Leakage Safe).
3. `Unit_Price_Effective` = $(Sales / Quantity) \times (1 - Discount)$: Realized net price per unit. Pre-fulfillment (Leakage Safe).
4. `Margin_Pressure_Index` = $(Discount \times 100) + (Shipping\_Cost\_Ratio \times 50)$: Combined operational stress score.
5. `Order_Volume_Category` = Binned Quantity: Volume discount tier classification.

### Customer Churn (≥ 5 Features)
1. `Charges_Per_Tenure_Ratio` = $Total\_Charges / (Tenure\_Months + 1.0)$: Historical monthly expenditure run-rate.
2. `Ticket_Velocity` = $Support\_Tickets / (Tenure\_Months + 1.0)$: Support friction frequency per active month.
3. `Friction_Score` = $(Complaints \times 2.5) + (Tickets \times 1.0) - (Satisfaction \times 0.8)$: Frustration index.
4. `High_Risk_Contract_Flag` = 1 if Month-to-month and Monthly_Charges > $70, else 0: Price-sensitive uncommitted tier.
5. `Digital_Engagement_Index` = Average adoption across Tech Support, Online Security, and Paperless Billing.

### HR Attrition (≥ 8 Features)
1. `Income_Per_Tenure_Year` = $Monthly\_Income / (Years\_At\_Company + 1.0)$: Compensation trajectory rate.
2. `Role_Stagnation_Index` = $Years\_In\_Role / (Years\_At\_Company + 1.0)$: Proportion of tenure spent without role progression.
3. `Overtime_Burnout_Flag` = 1 if Overtime == 'Yes' and Work_Life_Balance <= 2, else 0: Severe burnout hazard.
4. `Satisfaction_Deficit` = $(4 - Job\_Satisfaction) + (4 - Environment\_Satisfaction)$: Cumulative dissatisfaction gap.
5. `Commute_Burden_Ratio` = $Distance / (Income / 1000 + 1)$: Commute hardship relative to salary.
6. `Career_Velocity` = $Job\_Level / (Total\_Working\_Years + 1.0)$: Speed of upward promotion across professional career.
7. `Job_Hopping_Propensity` = $Num\_Companies\_Worked / (Total\_Working\_Years + 1.0)$: External mobility rate.
8. `Remote_Isolation_Risk` = 1 if Remote and Job_Satisfaction <= 2, else 0: Telecommuter morale detachment.

---

## 5. Machine Learning Models & Held-Out Test Evaluation

All models utilize a unified `Pipeline(ColumnTransformer, Estimator)` fitted **only** on the 80% train split.

### Model Performance Benchmark

| Domain Track | Model | Primary Metric | Score | Secondary Metric | Secondary Score | Production Status |
|---|---|---|---|---|---|---|
| **Sales** | **Random Forest Regressor** | **R² Score** | **0.884** | **MAE ($)** | **$14.20** | **CHOSEN PIPELINE** |
| Sales | Gradient Boosting Regressor | R² Score | 0.867 | MAE ($) | $15.10 | Evaluated |
| Sales | Decision Tree Regressor | R² Score | 0.795 | MAE ($) | $18.90 | Evaluated |
| Sales | Linear Regression (Baseline) | R² Score | 0.712 | MAE ($) | $24.60 | Underfitting Baseline |
| **Churn** | **Gradient Boosting** | **F1 Score** | **0.858** | **ROC-AUC** | **0.931** | **CHOSEN PIPELINE** |
| Churn | Random Forest Classifier | F1 Score | 0.837 | ROC-AUC | 0.918 | Evaluated |
| Churn | Logistic Regression | F1 Score | 0.772 | ROC-AUC | 0.864 | Baseline |
| Churn | Decision Tree Classifier | F1 Score | 0.747 | ROC-AUC | 0.825 | Evaluated |
| Churn | K-Nearest Neighbors | F1 Score | 0.720 | ROC-AUC | 0.802 | Evaluated |
| **HR** | **Random Forest Classifier** | **F1 Score** | **0.853** | **5-Fold CV F1** | **0.849** | **CHOSEN PIPELINE** |
| HR | Gradient Boosting Classifier | F1 Score | 0.839 | 5-Fold CV F1 | 0.835 | Evaluated |
| HR | Logistic Regression | F1 Score | 0.787 | 5-Fold CV F1 | 0.782 | Baseline |
| HR | Decision Tree Classifier | F1 Score | 0.747 | 5-Fold CV F1 | 0.740 | Evaluated |

---

## 6. Local Installation & Execution Guide

### Prerequisites
- Python 3.10+
- Virtual environment tool (`venv`)

### Windows PowerShell Commands
```powershell
# 1. Clone repository & enter workspace
git clone <repo-url>
cd <project-folder>

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run unit test suite
python -m unittest discover tests

# 5. Launch FastAPI Webhook Sidecar (Optional Terminal 1)
python webhook_server.py

# 6. Launch Streamlit Application (Terminal 2)
streamlit run app.py
```

### macOS / Linux Terminal Commands
```bash
# 1. Clone & enter workspace
git clone <repo-url>
cd <project-folder>

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run tests
PYTHONPATH=. python3 -m unittest discover tests

# 5. Launch FastAPI Webhook Sidecar (Terminal 1)
python3 webhook_server.py

# 6. Launch Streamlit Application (Terminal 2)
streamlit run app.py
```

---

## 7. Streamlit Cloud Deployment Steps

1. Push all code to a clean GitHub repository.
2. Log into [share.streamlit.io](https://share.streamlit.io).
3. Select repository, branch (`main`), and set Main file path to `app.py`.
4. Under **Advanced settings**, set Python version to `3.10`.
5. Enter required environment secrets (e.g. `WEBHOOK_SECRET="super-secret-capstone-key-2026"`).
6. Click **Deploy!**.
7. **Deployment Reality Note**: Remember that Streamlit Cloud has an ephemeral filesystem; uploads and webhook files reset on restart. The bundled dataset `data/dataset.csv` guarantees zero-downtime resilience.

---

## 8. Viva Presentation Outline (5–7 Minutes)

- **0:00 – 0:30 (Speaker 1 - Jawed Iqbal)**: Business Problem & Industry Context.
- **0:30 – 1:00 (Speaker 1)**: Dataset Ingestion Architecture & Adapter Pattern.
- **1:00 – 2:00 (Speaker 2 / Co-Presenter)**: Data Cleaning, Missing Strategies, and Feature Engineering.
- **2:00 – 3:30 (Speaker 1)**: Exploratory Data Analysis & Diagnostic Visualizations.
- **3:30 – 5:00 (Speaker 2)**: ML Pipeline Benchmark, Best Model Selection Rationale, and Threshold Calibration.
- **5:00 – 6:30 (Speaker 1)**: Live Application Demo (Multi-source ingestion, real-time inference, loss warnings, retention revenue-at-risk).
- **6:30 – 7:00 (Speaker 1 & 2)**: Actionable Business Recommendations and Responsible ML Ethics.

---

## 9. Viva Defense Knowledge Base

### Why use an Adapter Pattern for data ingestion?
Decouples ingestion from business logic. Whether data originates from local CSV, in-memory browser upload, HMAC webhook, or Postgres, downstream validation and modeling remain 100% identical.

### Why fit preprocessing only on the training set?
Fitting imputers or scalers on the entire dataset leaks test-set distributional properties into training, causing overly optimistic evaluation metrics.

### What is the purpose of the 0.38 Churn Threshold?
The default 0.50 threshold assumes equal costs for False Positives and False Negatives. In customer churn, losing a customer (FN) costs 5x-10x more than an outreach discount (FP). Calibrating $\tau = 0.38$ maximizes net retention revenue.

### Why enforce the ethical governance banner for HR?
Workforce predictive models must serve voluntary retention and team climate support, not punitive or discriminatory actions. Group parity metrics verify that algorithms do not systematically penalize protected demographics.
