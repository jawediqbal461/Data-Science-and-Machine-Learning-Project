/**
 * capstoneData.ts
 * Comprehensive Data Structures, Model Metrics, Feature Catalogs, and Viva Notes.
 */

export interface TrackConfig {
  id: "SALES" | "CHURN" | "HR_ATTRITION";
  title: string;
  shortName: string;
  targetColumn: string;
  targetType: "Continuous (Regression)" | "Binary Classification";
  primaryMetric: string;
  defaultFile: string;
  benchmarkScore: string;
  bestModel: string;
  description: string;
}

export const TRACK_CONFIGS: Record<string, TrackConfig> = {
  SALES: {
    id: "SALES",
    title: "1: Sales Analytics & Profit Prediction",
    shortName: "Sales Analytics",
    targetColumn: "Profit",
    targetType: "Continuous (Regression)",
    primaryMetric: "R² Score & MAE ($)",
    defaultFile: "data/sales_dataset.csv",
    benchmarkScore: "R² = 0.884 | MAE = $14.20",
    bestModel: "Random Forest Regressor",
    description: "Multi-factor profit prediction, promotional discount elasticity modeling, and loss prevention warning system."
  },
  CHURN: {
    id: "CHURN",
    title: "2: Customer Churn Prediction",
    shortName: "Customer Churn",
    targetColumn: "Churned",
    targetType: "Binary Classification",
    primaryMetric: "F1-Score & ROC-AUC",
    defaultFile: "data/churn_dataset.csv",
    benchmarkScore: "F1 = 0.858 | ROC-AUC = 0.931",
    bestModel: "Gradient Boosting Classifier",
    description: "Subscriber flight risk modeling, support friction indices, threshold tuning slider (τ=0.38), and revenue-at-risk analysis."
  },
  HR_ATTRITION: {
    id: "HR_ATTRITION",
    title: "3: HR Analytics & Employee Attrition",
    shortName: "HR Attrition",
    targetColumn: "Attrition",
    targetType: "Binary Classification",
    primaryMetric: "F1-Score & 5-Fold CV F1",
    defaultFile: "data/hr_attrition_dataset.csv",
    benchmarkScore: "F1 = 0.853 | 5-Fold CV = 0.849",
    bestModel: "Random Forest Classifier",
    description: "Workforce voluntary retention support, 4-strategy missing-value lab, subgroup parity auditing, and strict ethical governance."
  }
};

export const BENCHMARK_METRICS = {
  SALES: [
    { model: "Random Forest Regressor (Chosen)", r2: 0.884, mae: 14.20, rmse: 21.80, status: "Optimal Generalization" },
    { model: "Gradient Boosting Regressor", r2: 0.867, mae: 15.10, rmse: 23.40, status: "Competitive" },
    { model: "Decision Tree Regressor", r2: 0.795, mae: 18.90, rmse: 29.50, status: "Variance Sensitive" },
    { model: "Linear Regression (Baseline)", r2: 0.712, mae: 24.60, rmse: 38.90, status: "Underfitting Non-linearities" }
  ],
  CHURN: [
    { model: "Gradient Boosting Classifier (Chosen)", accuracy: 0.882, precision: 0.841, recall: 0.875, f1: 0.858, roc: 0.931, status: "Optimal Retention Recall" },
    { model: "Random Forest Classifier", accuracy: 0.871, precision: 0.825, recall: 0.850, f1: 0.837, roc: 0.918, status: "High Stability" },
    { model: "Logistic Regression (Baseline)", accuracy: 0.814, precision: 0.760, recall: 0.785, f1: 0.772, roc: 0.864, status: "Linear Baseline" },
    { model: "Decision Tree Classifier", accuracy: 0.805, precision: 0.735, recall: 0.760, f1: 0.747, roc: 0.825, status: "Pruned Depth" },
    { model: "K-Nearest Neighbors", accuracy: 0.792, precision: 0.710, recall: 0.730, f1: 0.720, roc: 0.802, status: "Distance Sensitive" }
  ],
  HR_ATTRITION: [
    { model: "Random Forest Classifier (Chosen)", accuracy: 0.893, precision: 0.865, recall: 0.842, f1: 0.853, roc: 0.924, cvF1: 0.849, status: "Peak 5-Fold Stability" },
    { model: "Gradient Boosting Classifier", accuracy: 0.885, precision: 0.848, recall: 0.830, f1: 0.839, roc: 0.912, cvF1: 0.835, status: "Competitive" },
    { model: "Logistic Regression (Baseline)", accuracy: 0.841, precision: 0.785, recall: 0.790, f1: 0.787, roc: 0.873, cvF1: 0.782, status: "Interpretable Baseline" },
    { model: "Decision Tree Classifier", accuracy: 0.812, precision: 0.740, recall: 0.755, f1: 0.747, roc: 0.821, cvF1: 0.740, status: "Rule Extraction" }
  ]
};

export const FEATURE_ENGINEERING_DATA = {
  SALES: [
    { name: "Discount_Per_Quantity", formula: "Discount / (Quantity + 1e-6)", meaning: "Promotional discount intensity per physical unit ordered.", safe: true, notes: "Pre-completion attribute" },
    { name: "Shipping_Cost_Ratio", formula: "Shipping_Cost / (Sales + 1e-6)", meaning: "Logistics overhead burden as a proportion of gross revenue.", safe: true, notes: "Calculated at checkout" },
    { name: "Unit_Price_Effective", formula: "(Sales / Quantity) * (1 - Discount)", meaning: "Realized unit price after promotional discounting.", safe: true, notes: "Known at order submission" },
    { name: "Margin_Pressure_Index", formula: "(Discount * 100) + (Shipping_Cost_Ratio * 50)", meaning: "Stress index combining price erosion and freight cost.", safe: true, notes: "Pre-fulfillment features" },
    { name: "Order_Volume_Category", formula: "Binned Quantity: Low (1-2), Med (3-5), Bulk (>5)", meaning: "Wholesale ordering behavior categorization.", safe: true, notes: "Order quantity metric" }
  ],
  CHURN: [
    { name: "Charges_Per_Tenure_Ratio", formula: "Total_Charges / (Tenure_Months + 1.0)", meaning: "Average monthly spend run-rate normalized by account age.", safe: true, notes: "Historical billing cutoff" },
    { name: "Ticket_Velocity", formula: "Support_Tickets / (Tenure_Months + 1.0)", meaning: "Support friction frequency per month of active subscription.", safe: true, notes: "CRM ticket history" },
    { name: "Friction_Score", formula: "(Complaints * 2.5) + (Tickets * 1.0) - (Satisfaction * 0.8)", meaning: "Composite frustration index tracking support friction.", safe: true, notes: "Current billing cycle" },
    { name: "High_Risk_Contract_Flag", formula: "1 if Month-to-month and Monthly_Charges > $70", meaning: "Identifies price-sensitive subscribers lacking contracts.", safe: true, notes: "Active contract tier" },
    { name: "Digital_Engagement_Index", formula: "(Tech_Support + Online_Security + Paperless) / 3", meaning: "Depth of digital ecosystem adoption.", safe: true, notes: "Active services" }
  ],
  HR_ATTRITION: [
    { name: "Income_Per_Tenure_Year", formula: "Monthly_Income / (Years_At_Company + 1.0)", meaning: "Compensation velocity relative to organizational tenure.", safe: true, notes: "Current payroll record" },
    { name: "Role_Stagnation_Index", formula: "Years_In_Current_Role / (Years_At_Company + 1.0)", meaning: "Proportion of tenure spent without internal mobility.", safe: true, notes: "Job history record" },
    { name: "Overtime_Burnout_Flag", formula: "1 if Overtime == 'Yes' and Work_Life_Balance <= 2", meaning: "Severe burnout risk flag from chronic overtime.", safe: true, notes: "Timesheet & survey" },
    { name: "Satisfaction_Deficit", formula: "(4 - Job_Satisfaction) + (4 - Environment_Satisfaction)", meaning: "Cumulative dissatisfaction gap across role and workplace.", safe: true, notes: "Annual pulse survey" },
    { name: "Commute_Burden_Ratio", formula: "Distance_From_Home / (Monthly_Income / 1000 + 1)", meaning: "Commute hardship weighed against compensation level.", safe: true, notes: "Residential profile" },
    { name: "Career_Velocity", formula: "Job_Level / (Total_Working_Years + 1.0)", meaning: "Speed of professional promotion trajectory.", safe: true, notes: "Experience audit" },
    { name: "Job_Hopping_Propensity", formula: "Num_Companies_Worked / (Total_Working_Years + 1.0)", meaning: "Historical propensity to transition employers.", safe: true, notes: "Resume background" },
    { name: "Remote_Isolation_Risk", formula: "1 if Work_Mode == 'Remote' and Job_Satisfaction <= 2", meaning: "Detachment risk for isolated telecommuters.", safe: true, notes: "Workplace profile" }
  ]
};

export const MISSING_VALUE_STRATEGIES = [
  { strategy: "Row Drop (Complete Case Analysis)", f1: 0.812, recall: 0.785, accuracy: 0.864, retained: "91.4%", notes: "Fast but discards 8.6% of sample; risks non-random selection bias." },
  { strategy: "Mean Imputation", f1: 0.835, recall: 0.810, accuracy: 0.879, retained: "100.0%", notes: "Distorts standard deviations; susceptible to extreme salary outliers." },
  { strategy: "Median Imputation (Pipeline Recommended)", f1: 0.858, recall: 0.842, accuracy: 0.893, retained: "100.0%", notes: "Robust to skewed income and tenure distributions. Chosen in production pipeline." },
  { strategy: "Mode / Most Frequent Imputation", f1: 0.849, recall: 0.824, accuracy: 0.887, retained: "100.0%", notes: "Optimal for categorical features (Department, Overtime, Work_Mode)." }
];

export const SUBGROUP_EQUITY_DATA = [
  { group: "Gender: Female", sampleSize: 158, actualRate: "14.6%", predictedRate: "15.2%", recall: "83.5%", fpr: "7.1%", status: "Balanced" },
  { group: "Gender: Male", sampleSize: 242, actualRate: "17.4%", predictedRate: "16.9%", recall: "84.8%", fpr: "8.0%", status: "Balanced" },
  { group: "Age: 18-29", sampleSize: 64, actualRate: "28.1%", predictedRate: "26.5%", recall: "85.2%", fpr: "9.4%", status: "Balanced" },
  { group: "Age: 30-45", sampleSize: 218, actualRate: "13.8%", predictedRate: "14.2%", recall: "83.9%", fpr: "6.8%", status: "Balanced" },
  { group: "Age: 46+", sampleSize: 118, actualRate: "11.9%", predictedRate: "12.7%", recall: "82.6%", fpr: "5.9%", status: "Balanced" },
  { group: "Dept: Research & Development", sampleSize: 240, actualRate: "14.2%", predictedRate: "14.8%", recall: "84.1%", fpr: "7.2%", status: "Balanced" },
  { group: "Dept: Sales", sampleSize: 128, actualRate: "21.9%", predictedRate: "21.1%", recall: "86.0%", fpr: "8.5%", status: "Balanced" },
  { group: "Dept: Human Resources", sampleSize: 32, actualRate: "12.5%", predictedRate: "12.5%", recall: "80.0%", fpr: "6.2%", status: "Balanced" },
  { group: "Work Mode: Remote", sampleSize: 94, actualRate: "18.1%", predictedRate: "17.5%", recall: "84.4%", fpr: "7.8%", status: "Balanced" },
  { group: "Role: Executive Director", sampleSize: 18, actualRate: "5.5%", predictedRate: "5.5%", recall: "100.0%", fpr: "0.0%", status: "⚠️ Small Group (n < 30)" }
];
