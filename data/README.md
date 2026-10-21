# Dataset Provenance & Data Ingestion Guidelines

This repository supports multi-source data ingestion for the Data Science and Machine Learning Capstone Assignment by **Jawed Iqbal**.

## Supported Datasets

1. **Sales Analytics & Profit Prediction** (`data/sales_dataset.csv`):
   - **Target**: `Profit` (USD continuous)
   - **Key Features**: `Sales`, `Quantity`, `Discount`, `Shipping_Cost`, `Region`, `Category`, `Sub_Category`, `Ship_Mode`
   - **Post-Completion Exclusions**: `Customer_Rating`, `Returned`, `Total_Sale` (excluded from pre-fulfillment modeling to avoid temporal leakage).
   - **Identifiers**: `Order_ID`, `Customer_ID`, `Customer_Name` (excluded for privacy & leakage).

2. **Customer Churn Prediction** (`data/churn_dataset.csv`):
   - **Target**: `Churned` (1 = Yes, 0 = No)
   - **Key Features**: `Tenure_Months`, `Contract_Type`, `Monthly_Charges`, `Total_Charges`, `Payment_Method`, `Support_Tickets`, `Complaints`, `Satisfaction_Score`, `NPS`
   - **Identifiers**: `Customer_ID`, `Customer_Name`, `Signup_Date` (excluded).

3. **HR Analytics & Employee Attrition** (`data/hr_attrition_dataset.csv`):
   - **Target**: `Attrition` (1 = Yes, 0 = No)
   - **Key Features**: `Age`, `Gender`, `Department`, `Job_Role`, `Monthly_Income`, `Job_Level`, `Years_At_Company`, `Years_In_Current_Role`, `Overtime`, `Work_Life_Balance`, `Job_Satisfaction`, `Environment_Satisfaction`, `Distance_From_Home`, `Work_Mode`
   - **Identifiers**: `Employee_ID`, `Employee_Name`, `Hire_Date` (excluded).
   - **Mandatory Policy**: Workforce-level retention and voluntary support only. Never for individual termination/disciplinary actions.

## Ingestion Modes Supported
- **Bundled CSV (`BundledCSVSource`)**: Cold-start archive at `data/dataset.csv`.
- **User Upload (`UploadedFileSource`)**: In-memory session upload via web interface with column-mapping validator.
- **Webhook Ingest (`WebhookPushSource`)**: HMAC-SHA256 authenticated drop zone in `data/incoming/`.
- **Database Read-Only (`DatabaseReadOnlySource`)**: Postgres/Supabase SQL SELECT.
- **REST API Pull (`RestAPIPullSource`)**: Authenticated endpoint streaming.
