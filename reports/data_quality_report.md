# Comprehensive Data Quality & Profiling Report

**Student:** Jawed Iqbal  
**Course:** Data Science and Machine Learning  
**Project:** Data Science Capstone (Multi-Source Data Ingestion)  
**Date:** October 2026  

---

## 1. Executive Summary

This report establishes the data provenance, ingestion pipeline validation, and data quality profiling across the three project domains:
1. **Sales Analytics and Profit Prediction**
2. **Customer Churn Prediction**
3. **HR Analytics and Employee Attrition**

All data streams are routed through an abstract `DataSource` interface with strict cryptographic verification (SHA-256) and schema gating.

---

## 2. Ingestion Pipeline & Adapter Audits

| Ingestion Source | Medium / Protocol | Cryptographic Integrity | State Isolation | Status |
|---|---|---|---|---|
| `BundledCSVSource` | Disk read (`data/dataset.csv`) | SHA-256 hash validation | Read-only cold-start default | Active |
| `UploadedFileSource` | Web in-memory buffer | Dynamic byte hash check | Isolated per-session state | Active |
| `WebhookPushSource` | FastAPI sidecar (`/webhook/ingest`) | HMAC-SHA256 signature verification | Isolated drop zone (`data/incoming/`) | Active |
| `DatabaseReadOnlySource` | SQL SELECT via `st.secrets` | Read-only constraint | Parameterized query safe | Ready |
| `RestAPIPullSource` | HTTPS REST endpoint | Bearer token authorization | In-memory stream parse | Ready |

---

## 3. Data Profiling & Quality Metrics

### 3.1 Sales Analytics Dataset
- **Total Records:** 400
- **Total Features:** 16 (12 predictors, 1 target: `Profit`, 3 leakage-isolated columns)
- **Duplicate Rows:** 0 (0.0%)
- **Missing Values:** 0 null values across all fields
- **Temporal Coverage:** 2026-08-01 through 2026-08-28
- **Excluded Features:** `Order_ID`, `Customer_ID`, `Customer_Name` (privacy); `Customer_Rating`, `Returned`, `Total_Sale` (post-completion temporal leakage).

### 3.2 Customer Churn Dataset
- **Total Records:** 400
- **Target Distribution:** 73.5% Non-Churn (`No`), 26.5% Churned (`Yes`)
- **Missing Values:** 0 null values
- **Excluded Features:** `Customer_ID`, `Customer_Name`, `Signup_Date`

### 3.3 HR Attrition Dataset
- **Total Records:** 400
- **Target Distribution:** 83.8% Retained (`No`), 16.2% Attrited (`Yes`)
- **Missing Values:** Evaluated across 4 imputation pipelines (Row-drop, Mean, Median, Mode)
- **Excluded Features:** `Employee_ID`, `Employee_Name`, `Hire_Date`

---

## 4. Schema Gate & Column-Mapping Protocols

When non-standard datasets are uploaded:
1. `validate_dataset` checks for column presence.
2. If canonical columns are missing, automatic string similarity heuristics generate mapping suggestions.
3. If the prediction target is absent, ML training is disabled.
4. Silent column renaming is strictly prohibited.
