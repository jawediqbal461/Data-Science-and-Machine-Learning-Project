import React, { useRef } from "react";
import { useData } from "../context/DataContext";
import {
  Home,
  Database,
  BarChart3,
  Sliders,
  Cpu,
  Zap,
  Lightbulb,
  ShieldAlert,
  Code,
  GraduationCap,
  Upload,
  Radio,
  Server,
  Globe,
  RefreshCw,
  FileSpreadsheet,
  AlertOctagon,
  Users
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const {
    activeTrack,
    trackConfig,
    activeSource,
    setActiveSource,
    activePage,
    setActivePage,
    meta,
    reloadBundled,
    simulateWebhookPush,
    handleFileUpload,
    webhookStatus,
    setIsUploadModalOpen
  } = useData();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const navItems = [
    { id: "home", label: "1. Home & Architecture", icon: Home },
    { id: "global_overview", label: "2. Global Data Overview", icon: Globe },
    { id: "explorer", label: "3. Data Explorer & Schema", icon: Database },
    { id: "eda", label: "4. EDA & Visualizations", icon: BarChart3 },
    { id: "features", label: "5. Preprocessing & Features", icon: Sliders },
    { id: "models", label: "6. ML Pipeline Studio", icon: Cpu },
    { id: "inference", label: "7. Real-Time Prediction", icon: Zap },
    ...(activeTrack === "CHURN"
      ? [{ id: "retention", label: "8. Retention Dashboard", icon: Users }]
      : []),
    { id: "recommendations", label: "9. Recommendations", icon: Lightbulb },
    { id: "responsible_ml", label: "10. Responsible ML & Ethics", icon: ShieldAlert },
    { id: "code", label: "11. Repository Code Viewer", icon: Code },
    { id: "viva", label: "12. Viva Defense Mentor", icon: GraduationCap }
  ];

  const handleNativeFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      if (!text) return;
      const lines = text.trim().split("\n");
      if (lines.length <= 1) return;
      const headers = lines[0].split(",").map((h) => h.trim());
      const parsedRows = lines.slice(1).map((line) => {
        const vals = line.split(",").map((v) => v.trim());
        const row: Record<string, any> = {};
        headers.forEach((h, idx) => {
          const val = vals[idx];
          row[h] = !isNaN(Number(val)) && val !== "" ? Number(val) : val;
        });
        return row;
      });
      handleFileUpload(file.name, parsedRows);
    };
    reader.readAsText(file);
  };

  return (
    <aside className="w-72 lg:w-80 shrink-0 bg-slate-950/80 border-r border-slate-800 flex flex-col h-[calc(100vh-68px)] overflow-y-auto p-4 custom-scrollbar">
      {/* Track Badge */}
      <div className="mb-4 p-3 rounded-xl bg-gradient-to-r from-slate-900 to-blue-950 border border-slate-800">
        <div className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
          Active Capstone Track
        </div>
        <div className="font-bold text-sm text-slate-200 mt-0.5">
          {trackConfig.shortName}
        </div>
        <div className="text-xs text-blue-400 font-mono mt-1 font-semibold">
          Target: {trackConfig.targetColumn}
        </div>
      </div>

      {/* Quick Upload Action Button */}
      <button
        onClick={() => setIsUploadModalOpen(true)}
        className="mb-5 w-full p-2.5 rounded-xl bg-gradient-to-r from-blue-600/20 via-blue-500/15 to-indigo-600/20 hover:from-blue-600/30 hover:to-indigo-600/30 border border-blue-500/40 hover:border-blue-400 text-blue-200 text-xs font-bold flex items-center justify-between shadow-sm transition-all group cursor-pointer"
      >
        <div className="flex items-center gap-2">
          <Upload className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
          <span>Upload Dataset</span>
        </div>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/30 text-blue-300 font-mono">
          CSV / Excel
        </span>
      </button>

      {/* Navigation Pages */}
      <div className="mb-6">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors text-left cursor-pointer ${
                  isActive
                    ? "bg-blue-600 text-white font-semibold shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Data Ingestion Mode (§2) */}
      <div className="mb-6 pt-4 border-t border-slate-800/80">
        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 px-1 flex items-center justify-between">
          <span>Data Ingestion Mode</span>
          <span className="text-[10px] text-blue-400 font-semibold">§2 Ingestion</span>
        </div>

        <div className="space-y-1.5">
          {/* 1. Bundled */}
          <button
            onClick={() => setActiveSource("bundled")}
            className={`w-full p-2.5 rounded-lg border text-left transition-all cursor-pointer ${
              activeSource === "bundled"
                ? "bg-blue-950/40 border-blue-500/80 text-blue-200"
                : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-semibold">1. Bundled CSV Archive</span>
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5 truncate">Default cold start (data/dataset.csv)</div>
          </button>

          {/* 2. Uploaded File */}
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className={`w-full p-2.5 rounded-lg border text-left transition-all cursor-pointer ${
              activeSource === "upload"
                ? "bg-emerald-950/40 border-emerald-500/80 text-emerald-200 ring-1 ring-emerald-500/30"
                : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Upload className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs font-semibold">2. Upload Manual Data</span>
              </div>
              <span className="text-[10px] bg-emerald-900/40 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-700/60">
                CSV/XLSX
              </span>
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5 truncate">
              {activeSource === "upload" ? "Active Uploaded Dataset" : "Click to upload & clean CSV file"}
            </div>
          </button>

          {/* 3. Webhook Push */}
          <button
            onClick={simulateWebhookPush}
            className={`w-full p-2.5 rounded-lg border text-left transition-all ${
              activeSource === "webhook"
                ? "bg-purple-950/40 border-purple-500/80 text-purple-200"
                : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-xs font-semibold">3. WebhookPushSource</span>
              </div>
              <span className="text-[10px] bg-purple-900/60 text-purple-300 px-1.5 py-0.2 rounded border border-purple-700">
                HMAC
              </span>
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5 truncate">Simulate FastAPI sidecar push</div>
          </button>

          {/* 4. Database */}
          <button
            onClick={() => setActiveSource("database")}
            className={`w-full p-2.5 rounded-lg border text-left transition-all ${
              activeSource === "database"
                ? "bg-amber-950/40 border-amber-500/80 text-amber-200"
                : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center gap-2">
              <Server className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs font-semibold">4. DatabaseReadOnly</span>
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5 truncate">SQL SELECT via st.secrets</div>
          </button>

          {/* 5. REST API */}
          <button
            onClick={() => setActiveSource("api")}
            className={`w-full p-2.5 rounded-lg border text-left transition-all ${
              activeSource === "api"
                ? "bg-sky-950/40 border-sky-500/80 text-sky-200"
                : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center gap-2">
              <Globe className="w-3.5 h-3.5 text-sky-400" />
              <span className="text-xs font-semibold">5. RestAPIPullSource</span>
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5 truncate">JSON/CSV endpoint pull</div>
          </button>
        </div>
      </div>

      {/* Active Source Details (§2.1 describe) */}
      <div className="mb-4 p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs">
        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1 font-semibold">
          Source Metadata (§2.1)
        </div>
        <div className="text-slate-300 font-medium break-all mb-1.5 leading-snug">
          {meta.source_label}
        </div>
        <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-400 font-mono mb-2">
          <div>Rows: <span className="text-white font-semibold">{meta.row_count}</span></div>
          <div>Cols: <span className="text-white font-semibold">{meta.column_count}</span></div>
        </div>
        <div className="text-[10px] text-slate-500 font-mono truncate" title={meta.sha256}>
          SHA256: {meta.sha256.substring(0, 16)}...
        </div>

        <button
          onClick={reloadBundled}
          className="w-full mt-2 py-1.5 px-2 bg-slate-800 hover:bg-slate-700 rounded text-slate-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
        >
          <RefreshCw className="w-3 h-3 text-blue-400" />
          Reload Bundled Data
        </button>
      </div>

      {/* Streamlit Cloud Ephemeral Filesystem Notice (§2.5) */}
      <div className="mt-auto p-3 rounded-xl bg-amber-950/30 border border-amber-700/40 text-amber-200/90 text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-amber-400 mb-1">
          <AlertOctagon className="w-3.5 h-3.5 shrink-0" />
          <span>Deployment Constraint (§2.5)</span>
        </div>
        <p className="text-[11px] leading-relaxed text-amber-100/70">
          Streamlit Community Cloud has an ephemeral filesystem. Uploaded and webhook files do not survive restarts.
          Bundled dataset is always available.
        </p>
      </div>
    </aside>
  );
};
