import React, { useState } from "react";
import { useData } from "../context/DataContext";
import { Database, Download, AlertTriangle, CheckCircle2, ShieldCheck, Sparkles, FolderArchive, Terminal, Upload } from "lucide-react";
import JSZip from "jszip";

export const Header: React.FC = () => {
  const {
    activeTrack,
    setActiveTrack,
    trackConfig,
    activeSource,
    isMissingDataset,
    setIsMissingDataset,
    meta,
    reloadBundled,
    setIsUploadModalOpen
  } = useData();

  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownloadZip = async () => {
    setIsDownloading(true);
    try {
      const zip = new JSZip();

      // Bundle core code files
      zip.file(
        "requirements.txt",
        `streamlit>=1.35.0\npandas>=2.2.0\nnumpy>=1.26.0\nscikit-learn>=1.4.0\njoblib>=1.3.2\nmatplotlib>=3.8.0\nseaborn>=0.13.0\nplotly>=5.20.0\nopenpyxl>=3.1.2\nfastapi>=0.110.0\nuvicorn>=0.29.0\npytest>=8.1.0\nrequests>=2.31.0\n`
      );

      // Fetch or add README and python files
      zip.file(".streamlit/config.toml", `[theme]\nprimaryColor = "#2563EB"\nbackgroundColor = "#0F172A"\nsecondaryBackgroundColor = "#1E293B"\ntextColor = "#F8FAFC"\nfont = "sans serif"\n`);
      zip.file("data/incoming/.gitkeep", "");

      // Generate zip blob
      const content = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(content);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Jawed_Iqbal_DataScience_Capstone_${activeTrack}_Submission.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 4000);
    } catch (e) {
      console.error("Zip generation error:", e);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-40 px-4 lg:px-6 py-3 shadow-lg backdrop-blur-md bg-slate-900/95">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Title & Student Meta */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/20 text-white font-bold text-lg">
            DS
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-slate-100 text-base md:text-lg tracking-tight">
                Data Science & ML Capstone Platform
              </h1>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="font-semibold text-slate-300">Student: Jawed Iqbal</span>
              <span>•</span>
              <span>Course: Data Science & ML</span>
              <span>•</span>
              <span className="text-blue-400 font-medium">Deadline: 22 Oct 2026</span>
            </div>
          </div>
        </div>

        {/* Track Selector buttons */}
        <div className="flex items-center gap-1.5 p-1.5 bg-slate-950/80 rounded-xl border border-slate-800">
          {(["SALES", "CHURN", "HR_ATTRITION"] as const).map((trackKey) => {
            const isSelected = activeTrack === trackKey;
            const labels = {
              SALES: "1. Sales & Profit",
              CHURN: "2. Customer Churn",
              HR_ATTRITION: "3. HR Attrition"
            };
            return (
              <button
                key={trackKey}
                onClick={() => setActiveTrack(trackKey)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 flex items-center gap-1.5 ${
                  isSelected
                    ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                {labels[trackKey]}
                {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-sky-200 animate-pulse" />}
              </button>
            );
          })}
        </div>

        {/* Status Indicators & Action buttons */}
        <div className="flex items-center gap-2">
          {/* Missing dataset simulation toggle (Developer / Rubric Test Mode) */}
          <button
            onClick={() => setIsMissingDataset(!isMissingDataset)}
            title={
              isMissingDataset
                ? "Click to exit simulation and restore data"
                : "Developer test tool: Click to simulate what happens when dataset is missing"
            }
            className={`text-xs px-2.5 py-1.5 rounded-lg border font-medium flex items-center gap-1.5 transition-all cursor-pointer ${
              isMissingDataset
                ? "bg-rose-950/80 border-rose-500 text-rose-200 shadow-sm animate-pulse ring-1 ring-rose-500/50"
                : "bg-slate-850 hover:bg-slate-800 border-slate-700/80 text-slate-400 hover:text-slate-200"
            }`}
          >
            <AlertTriangle className={`w-3.5 h-3.5 shrink-0 ${isMissingDataset ? "text-rose-400" : "text-slate-500"}`} />
            <span className="hidden md:inline">
              {isMissingDataset ? "⚠️ Test Mode: No Data (Click to Restore)" : "🧪 Test Mode: Normal Data"}
            </span>
            <span className="md:hidden">
              {isMissingDataset ? "Test: Empty" : "Test: Normal"}
            </span>
          </button>

          {/* Upload Data Button (Prominent) */}
          <button
            onClick={() => setIsUploadModalOpen(true)}
            title="Upload manual CSV / Excel dataset (Sales, Churn, HR Attrition)"
            className="text-xs px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1.5 shadow-md shadow-blue-600/30 transition-all active:scale-95 cursor-pointer ring-1 ring-blue-400/40"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Dataset</span>
          </button>

          {/* Download Zip */}
          <button
            onClick={handleDownloadZip}
            disabled={isDownloading}
            className="text-xs px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center gap-1.5 shadow-sm transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isDownloading ? "Zipping..." : downloadSuccess ? "Downloaded! ✅" : "Download Zip"}</span>
          </button>
        </div>
      </div>

      {/* Target Column Strip */}
      <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="text-slate-500">Target Column:</span>
          <span className="px-2 py-0.5 rounded bg-blue-950/60 border border-blue-800 text-blue-300 font-mono font-medium">
            {trackConfig.targetColumn}
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-500">Benchmark Pipeline:</span>
          <span className="text-slate-300 font-medium">{trackConfig.bestModel}</span>
          <span className="text-emerald-400 font-mono">({trackConfig.benchmarkScore})</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-500">Active Source:</span>
          <span className="font-mono text-[11px] text-sky-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
            {meta.source_type} ({meta.row_count} rows, {meta.column_count} cols)
          </span>
        </div>
      </div>
    </header>
  );
};
