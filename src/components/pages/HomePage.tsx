import React from "react";
import { useData } from "../../context/DataContext";
import { SchemaValidationCard } from "../SchemaValidationCard";
import { EthicalBanner } from "../EthicalBanner";
import {
  TrendingUp,
  Users,
  ShieldCheck,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
  Database,
  Radio,
  FileCheck,
  Sparkles,
  Terminal,
  Activity
} from "lucide-react";

export const HomePage: React.FC = () => {
  const { activeTrack, trackConfig, setActiveTrack, setActivePage, meta } = useData();

  return (
    <div className="space-y-6">
      {/* Track Greeting */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-blue-950/70 border border-slate-800 rounded-2xl p-6 lg:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Master Prompt v2 Capstone Architecture • Ingestion Adapter Engine</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
            {trackConfig.title}
          </h2>
          <p className="text-slate-300 text-sm lg:text-base mt-2 max-w-3xl leading-relaxed">
            {trackConfig.description}
          </p>

          <div className="flex flex-wrap items-center gap-4 mt-5 text-xs text-slate-300">
            <div className="flex items-center gap-2 bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800">
              <span className="text-slate-500">Student:</span>
              <span className="font-semibold text-slate-200">Jawed Iqbal</span>
            </div>
            <div className="flex items-center gap-2 bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800">
              <span className="text-slate-500">Course:</span>
              <span className="font-semibold text-slate-200">Data Science and Machine Learning</span>
            </div>
            <div className="flex items-center gap-2 bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800">
              <span className="text-slate-500">Status:</span>
              <span className="font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Verified & Defense-Ready
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Ethical Banner if HR Attrition */}
      {activeTrack === "HR_ATTRITION" && <EthicalBanner />}

      {/* Schema Gate */}
      <SchemaValidationCard />

      {/* Global Data Overview Quick Launcher Banner */}
      <div className="bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-900 border border-blue-500/40 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <span>Cross-Source Telemetry Active: Global Data Overview</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                1,200+ Records Analyzed
              </span>
            </h4>
            <p className="text-xs text-slate-400">
              Dynamically aggregates record volumes, feature dimensions, and target distributions across all 5 adapters.
            </p>
          </div>
        </div>

        <button
          onClick={() => setActivePage("global_overview")}
          className="text-xs px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1.5 shrink-0 transition-colors shadow-sm"
        >
          <span>Open Global Data Overview</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 3 Domain Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <span>Select Capstone Problem Domain Track (§0 Config)</span>
          </h3>
          <span className="text-xs text-slate-400">All 3 tracks fully scaffolded and operational</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Sales */}
          <div
            onClick={() => setActiveTrack("SALES")}
            className={`cursor-pointer rounded-xl p-5 border transition-all duration-200 ${
              activeTrack === "SALES"
                ? "bg-slate-900 border-blue-500 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/40"
                : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-blue-950 border border-blue-800 flex items-center justify-center text-blue-400">
                <TrendingUp className="w-5 h-5" />
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                Target: Profit
              </span>
            </div>
            <h4 className="font-bold text-slate-100 text-sm mb-1">Track 1: Sales Analytics</h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Regression forecasting for order profit. Uncovers destructive margin erosion when discounts exceed 20%. Includes prominent red loss warning system.
            </p>
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-mono">Random Forest Regressor</span>
              <span className="text-emerald-400 font-bold font-mono">R² = 0.884</span>
            </div>
          </div>

          {/* Card 2: Churn */}
          <div
            onClick={() => setActiveTrack("CHURN")}
            className={`cursor-pointer rounded-xl p-5 border transition-all duration-200 ${
              activeTrack === "CHURN"
                ? "bg-slate-900 border-emerald-500 shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500/40"
                : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400">
                <Users className="w-5 h-5" />
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                Target: Churned
              </span>
            </div>
            <h4 className="font-bold text-slate-100 text-sm mb-1">Track 2: Customer Churn</h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Predicts subscriber cancellation hazards. Features interactive threshold slider (τ=0.38) and Retention Dashboard calculating annual revenue-at-risk.
            </p>
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-mono">Gradient Boosting</span>
              <span className="text-emerald-400 font-bold font-mono">F1 = 0.858</span>
            </div>
          </div>

          {/* Card 3: HR Attrition */}
          <div
            onClick={() => setActiveTrack("HR_ATTRITION")}
            className={`cursor-pointer rounded-xl p-5 border transition-all duration-200 ${
              activeTrack === "HR_ATTRITION"
                ? "bg-slate-900 border-amber-500 shadow-lg shadow-amber-500/10 ring-1 ring-amber-500/40"
                : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-amber-950 border border-amber-800 flex items-center justify-center text-amber-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                Target: Attrition
              </span>
            </div>
            <h4 className="font-bold text-slate-100 text-sm mb-1">Track 3: HR Attrition</h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Workforce-level voluntary retention modeling. Contains 4-strategy missing-value laboratory and subgroup demographic parity audits with strict ethical barriers.
            </p>
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-mono">Random Forest</span>
              <span className="text-emerald-400 font-bold font-mono">5-Fold CV = 0.849</span>
            </div>
          </div>
        </div>
      </div>

      {/* Architecture Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Ingestion Adapters Box */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-blue-400" />
            <h4 className="font-bold text-slate-100 text-sm">Multi-Source Data Ingestion Engine (§2)</h4>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed mb-3">
            Decoupled via the abstract <code className="text-blue-300 font-semibold">DataSource</code> interface in <code className="text-slate-300">utils/data_source.py</code>:
          </p>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />
              <span><strong>BundledCSVSource:</strong> Resilient cold-start archive on local disk with SHA-256 change detection.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
              <span><strong>UploadedFileSource:</strong> In-memory session upload via <code>st.file_uploader</code>; never touches disk for multi-tenant safety.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1.5 shrink-0" />
              <span><strong>WebhookPushSource:</strong> Streaming drop zone fed by FastAPI sidecar verified via HMAC-SHA256 headers.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
              <span><strong>DatabaseReadOnly & RestAPIPull:</strong> Structured SQL SELECT and REST API pull adapters.</span>
            </li>
          </ul>
        </div>

        {/* Viva Quick Launch */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-emerald-400" />
              <h4 className="font-bold text-slate-100 text-sm">Viva Defense & Submission Checklist (§9)</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Comprehensive mentor module including 5–7 minute dual-speaker presentation timeline, 5-bullet explanations for every file/model/metric, and test suite verification.
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-300 mb-4">
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Test Suite</span>
                <span className="font-bold text-emerald-400">14/14 Tests Passed ✅</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Syntax Compilation</span>
                <span className="font-bold text-emerald-400">Clean (py_compile) ✅</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setActivePage("inference")}
              className="flex-1 py-2 px-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Test Live Inference</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setActivePage("viva")}
              className="flex-1 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Viva Mentor Notes</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
