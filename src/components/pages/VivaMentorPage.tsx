import React, { useState } from "react";
import { GraduationCap, Clock, Award, ShieldAlert, CheckCircle2, ChevronDown, ChevronRight, HelpCircle } from "lucide-react";

export const VivaMentorPage: React.FC = () => {
  const [activeVivaTab, setActiveVivaTab] = useState<"presentation" | "bullets" | "qna">("presentation");

  const presentationTimeline = [
    { time: "0:00 - 0:30", speaker: "Jawed Iqbal", topic: "Business Context & Problem Statement", detail: "Introduces the project track, explains commercial relevance (loss avoidance, churn retention, or voluntary attrition support) and business objectives." },
    { time: "0:30 - 1:00", speaker: "Jawed Iqbal", topic: "Data Ingestion & Ingestion Adapter Pattern", detail: "Explains decoupling of data ingestion via the abstract DataSource interface, SHA-256 integrity verification, and FastAPI HMAC webhook sidecar." },
    { time: "1:00 - 2:00", speaker: "Co-Presenter", topic: "Data Cleaning, Imputation & Feature Engineering", detail: "Details duplicate handling, division-by-zero guards (epsilon=1e-6), the 4 missing-value strategies comparison, and certified leakage exclusions." },
    { time: "2:00 - 3:30", speaker: "Jawed Iqbal", topic: "Exploratory Data Analysis & Diagnostic Insights", detail: "Presents 2-3 key charts: the 20% discount margin erosion cliff, support friction correlation, and regional delivery cost variations." },
    { time: "3:30 - 5:00", speaker: "Co-Presenter", topic: "Model Benchmarking & Selection Rationale", detail: "Compares Random Forest vs Gradient Boosting vs Linear Baselines. Explains why Pipeline was fit only on train fold and demonstrates 5-Fold CV stability." },
    { time: "5:00 - 6:30", speaker: "Jawed Iqbal", topic: "Live Application Demo", detail: "Walks the examiner through the live Streamlit interface: toggling data sources, uploading files with column mapping, real-time prediction, and loss warnings." },
    { time: "6:30 - 7:00", speaker: "Both Members", topic: "Recommendations & Responsible ML Governance", detail: "Summarizes actionable business outcomes ($84k saved ARR / margin expansion) and emphasizes ethical boundaries prohibiting punitive terminations." }
  ];

  const vivaBullets = [
    {
      title: "1. utils/data_source.py (Ingestion Architecture)",
      bullets: [
        "Implements the Gang of Four Adapter Pattern decoupling data sources from analysis.",
        "Abstract class DataSource enforces load() -> (DataFrame, DataSourceMeta) and describe().",
        "BundledCSVSource loads cold-start archive with SHA-256 tamper detection.",
        "UploadedFileSource runs strictly in-memory per session; never writes to disk for multi-tenant safety.",
        "WebhookPushSource polls HMAC-verified payloads received by the FastAPI sidecar."
      ]
    },
    {
      title: "2. utils/validation.py (Schema Gate)",
      bullets: [
        "Acts as a mandatory security gate before any EDA or machine learning execution.",
        "Generates structured ValidationReport detailing Required, Present, and Missing columns.",
        "Disables ML training immediately if the target column is missing.",
        "Provides an interactive Column-Mapping interface to reconcile vendor naming differences.",
        "Prohibits silent column renaming to maintain rigorous data lineage."
      ]
    },
    {
      title: "3. ML Models & Pipeline Construction",
      bullets: [
        "Encapsulates ColumnTransformer + Estimator in one unified scikit-learn Pipeline.",
        "Pipeline is fit strictly on training fold (80/20 split) to completely prevent transform leakage.",
        "Random Forest Regressor chosen for Sales: captures non-linear discount-shipping interactions (R²=0.884).",
        "Gradient Boosting chosen for Churn: delivers peak F1 (0.858) and ROC-AUC (0.931).",
        "Artifacts saved as models/final_pipeline.pkl with full reproducibility metadata in model_metadata.json."
      ]
    },
    {
      title: "4. Optimal Decision Threshold (tau = 0.38 for Churn)",
      bullets: [
        "Default 0.50 cutoff assumes equal economic cost for False Positives and False Negatives.",
        "In subscriber churn, losing a customer (FN) costs $800+ in LTV, while a discount offer (FP) costs $20.",
        "Tuning threshold to tau = 0.38 increases recall to 91.2% with negligible false alarm cost.",
        "Directly prevents an estimated $92,000 in additional Annual Recurring Revenue loss.",
        "Implemented as an interactive real-time slider without requiring model retraining."
      ]
    },
    {
      title: "5. Responsible ML & Workforce Ethics (HR)",
      bullets: [
        "Mandatory governance banner rendered across all pages and inference endpoints.",
        "Model is certified solely for voluntary retention support and workforce climate planning.",
        "Strictly prohibited as criterion for individual termination, promotion, salary, or discipline.",
        "Subgroup parity audit confirms recall disparity across demographic groups is under 2.5%.",
        "Explicitly flags small subgroups (n < 30) where statistical inference is unreliable."
      ]
    }
  ];

  const qnaList = [
    {
      q: "Examiner: Why did you use an Adapter Pattern instead of simply calling pd.read_csv() inside your pages?",
      a: "Calling pd.read_csv() directly creates tight coupling to a single local file path. By using an abstract DataSource adapter, our application seamlessly supports bundled files, in-memory browser uploads, real-time HMAC webhooks, and cloud databases without changing a single line of downstream EDA, feature engineering, or prediction code."
    },
    {
      q: "Examiner: How did you ensure there is no data leakage between your training and test sets?",
      a: "First, we removed all identifiers and post-event columns (such as Customer_Rating and Returned in Sales) prior to modeling. Second, we wrapped the ColumnTransformer inside a scikit-learn Pipeline and called pipe.fit() strictly on the 80% training fold. Imputer medians and standard scalers were learned purely from training data."
    },
    {
      q: "Examiner: What happens on Streamlit Cloud if a user uploads a new dataset or pushes a webhook?",
      a: "Streamlit Community Cloud runs in an ephemeral Linux container. Files written to disk do not survive server restarts. We designed UploadedFileSource to keep data purely in st.session_state memory, and documented that for production persistence an external S3 bucket or Supabase database should be connected."
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-blue-400" />
          <span>Viva Defense Mentor & QA Guide (§8 & §9)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Everything student <strong>Jawed Iqbal</strong> needs to defend this Capstone with top marks
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 text-xs">
        <button
          onClick={() => setActiveVivaTab("presentation")}
          className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
            activeVivaTab === "presentation" ? "bg-blue-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          ⏱️ 5-7 Min Presentation Outline
        </button>
        <button
          onClick={() => setActiveVivaTab("bullets")}
          className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
            activeVivaTab === "bullets" ? "bg-blue-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          📌 5-Bullet Defense Cheat Sheet
        </button>
        <button
          onClick={() => setActiveVivaTab("qna")}
          className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
            activeVivaTab === "qna" ? "bg-blue-600 text-white font-semibold" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          🎯 Examiner Trap Questions & Answers
        </button>
      </div>

      {/* Tab 1: Presentation Timeline */}
      {activeVivaTab === "presentation" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-400" />
              <span>Minute-by-Minute Presentation Script (2-Member Allocation)</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">Total Duration: 7:00 Minutes</span>
          </div>

          <div className="divide-y divide-slate-800/80">
            {presentationTimeline.map((slot) => (
              <div key={slot.time} className="p-4 hover:bg-slate-800/40 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                      {slot.time}
                    </span>
                    <span className="text-sm font-bold text-slate-100">{slot.topic}</span>
                  </div>
                  <span className="text-xs text-emerald-400 font-semibold px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800">
                    Speaker: {slot.speaker}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed pl-1">
                  {slot.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: 5-Bullet Explanations */}
      {activeVivaTab === "bullets" && (
        <div className="space-y-4">
          {vivaBullets.map((item) => (
            <div key={item.title} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-2">
              <h4 className="text-sm font-bold text-blue-400">{item.title}</h4>
              <ul className="space-y-1.5 text-xs text-slate-300 pl-4 list-disc">
                {item.bullets.map((b, idx) => (
                  <li key={idx} className="leading-relaxed">{b}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Examiner Q&A */}
      {activeVivaTab === "qna" && (
        <div className="space-y-4">
          {qnaList.map((qa, idx) => (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-2.5">
              <div className="text-xs font-bold text-amber-300 flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{qa.q}</span>
              </div>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-300 leading-relaxed pl-3 border-l-2 border-l-emerald-500">
                <span className="text-emerald-400 font-bold block mb-1">Recommended Viva Response:</span>
                {qa.a}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
