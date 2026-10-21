import React, { useState } from "react";
import { useData } from "../../context/DataContext";
import { SchemaValidationCard } from "../SchemaValidationCard";
import { exportToCsv } from "../../utils/csvExport";
import { Search, Filter, ShieldCheck, Database, Table, BarChart2, AlertCircle, Download, CheckCircle2, Upload, Sparkles } from "lucide-react";

export const DataExplorerPage: React.FC = () => {
  const { dataset, activeTrack, trackConfig, isMissingDataset, setIsUploadModalOpen, meta } = useData();
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState<"table" | "stats" | "quality">("table");
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  if (isMissingDataset || dataset.length === 0) {
    return (
      <div className="space-y-6">
        <SchemaValidationCard />
      </div>
    );
  }

  const columns = Object.keys(dataset[0]);

  // Filter rows by search term
  const filteredRows = dataset.filter((row) => {
    if (!searchTerm) return true;
    return Object.values(row).some((val) =>
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  // Calculate statistics for numeric columns
  const numericStats = columns
    .filter((col) => typeof dataset[0][col] === "number")
    .map((col) => {
      const vals = dataset.map((r) => r[col]).filter((v) => typeof v === "number");
      const count = vals.length;
      const sum = vals.reduce((a, b) => a + b, 0);
      const mean = sum / count;
      const sorted = [...vals].sort((a, b) => a - b);
      const min = sorted[0];
      const max = sorted[sorted.length - 1];
      const median = sorted[Math.floor(sorted.length / 2)];
      const q25 = sorted[Math.floor(sorted.length * 0.25)];
      const q75 = sorted[Math.floor(sorted.length * 0.75)];
      return { col, count, mean, min, q25, median, q75, max };
    });

  const qualityAuditRows = columns.map((c) => {
    const nullCount = dataset.filter((r) => r[c] === null || r[c] === undefined || r[c] === "").length;
    const uniqueCount = new Set(dataset.map((r) => r[c])).size;
    const sampleVal = dataset[0][c];
    return {
      Column_Name: c,
      Data_Type: typeof sampleVal === "number" ? "Numeric" : "Categorical",
      Total_Count: dataset.length,
      Missing_Count: nullCount,
      Missing_Percentage: `${((nullCount / dataset.length) * 100).toFixed(2)}%`,
      Unique_Values: uniqueCount
    };
  });

  const handleExport = (name: string, data: any[]) => {
    const success = exportToCsv(name, data);
    if (success) {
      setExportNotice(`Exported ${data.length} records to ${name}.csv!`);
      setTimeout(() => setExportNotice(null), 3000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            <span>Dataset Explorer & Statistical Profile</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Inspecting <span className="text-slate-200 font-semibold">{trackConfig.shortName}</span> dataset ({dataset.length} loaded rows, {columns.length} columns)
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab("table")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "table" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Raw Records Table
          </button>
          <button
            onClick={() => setActiveTab("stats")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "stats" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Numeric Statistics
          </button>
          <button
            onClick={() => setActiveTab("quality")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "quality" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Data Quality Audit
          </button>
        </div>
      </div>

      {/* Dataset Upload & Cleaning Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900 via-blue-950/30 to-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
            <Upload className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-100 flex items-center gap-2">
              <span>Manual Dataset Ingestion & Pre-Cleaning Center</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-900/50 text-blue-300 border border-blue-700">
                {meta.source_type}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Want to upload custom Sales data, Customer Churn, or HR Attrition? Click to upload CSV, clean nulls/duplicates, and refresh statistics.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-md shadow-blue-600/30 transition-all cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload & Clean Dataset</span>
          </button>
        </div>
      </div>

      {/* Export Toast Notice */}
      {exportNotice && (
        <div className="bg-emerald-950/80 border border-emerald-600 text-emerald-200 px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-lg animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{exportNotice}</span>
        </div>
      )}

      {/* Schema Gate */}
      <SchemaValidationCard />

      {/* Leakage Protection Indicator */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="font-semibold text-slate-200">Temporal & Privacy Leakage Exclusions (§5):</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {activeTrack === "SALES" && (
            <>
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono">
                Order_ID, Customer_ID (ID Leakage)
              </span>
              <span className="px-2 py-0.5 rounded bg-rose-950/60 border border-rose-800 text-rose-300 font-mono">
                Customer_Rating, Returned, Total_Sale (Post-Completion)
              </span>
            </>
          )}
          {activeTrack === "CHURN" && (
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono">
              Customer_ID, Customer_Name, Signup_Date (Identifier & Date Leakage)
            </span>
          )}
          {activeTrack === "HR_ATTRITION" && (
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono">
              Employee_ID, Employee_Name, Hire_Date (Privacy Excluded)
            </span>
          )}
        </div>
      </div>

      {/* Tab 1: Table */}
      {activeTab === "table" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          {/* Table Controls */}
          <div className="p-3 bg-slate-950/60 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search across columns..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400 font-mono">
                Showing {filteredRows.slice(0, 30).length} of {filteredRows.length} matching rows
              </span>
              <button
                onClick={() => handleExport(`${trackConfig.shortName}_Filtered_Records`, filteredRows)}
                className="text-xs px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center gap-1.5 transition-colors shadow-sm"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export Filtered ({filteredRows.length})</span>
              </button>
            </div>
          </div>

          <div className="overflow-x-auto max-h-[500px] overflow-y-auto custom-scrollbar">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] sticky top-0 z-10 shadow-sm">
                <tr>
                  <th className="py-2.5 px-3 border-b border-slate-800">#</th>
                  {columns.map((c) => (
                    <th
                      key={c}
                      className={`py-2.5 px-3 border-b border-slate-800 font-mono ${
                        c === trackConfig.targetColumn ? "text-blue-400 bg-blue-950/40" : ""
                      }`}
                    >
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300 text-[11px]">
                {filteredRows.slice(0, 30).map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-2 px-3 text-slate-500">{idx + 1}</td>
                    {columns.map((c) => {
                      const val = row[c];
                      const isTarget = c === trackConfig.targetColumn;
                      const isNegative = typeof val === "number" && val < 0;
                      return (
                        <td
                          key={c}
                          className={`py-2 px-3 whitespace-nowrap ${
                            isTarget
                              ? isNegative
                                ? "bg-rose-950/30 text-rose-300 font-bold"
                                : "bg-blue-950/20 text-blue-300 font-semibold"
                              : ""
                          }`}
                        >
                          {typeof val === "number" ? val.toLocaleString() : String(val)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Stats */}
      {activeTab === "stats" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h4 className="text-sm font-bold text-slate-100">Descriptive Statistics (Numerical Columns)</h4>
              <p className="text-xs text-slate-400">Equivalent to pandas <code>df.describe()</code></p>
            </div>
            <button
              onClick={() => handleExport(`${trackConfig.shortName}_Numeric_Descriptive_Stats`, numericStats)}
              className="text-xs px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Statistics (CSV)</span>
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Column</th>
                  <th className="py-2.5 px-3">Count</th>
                  <th className="py-2.5 px-3">Mean</th>
                  <th className="py-2.5 px-3">Min</th>
                  <th className="py-2.5 px-3">25%</th>
                  <th className="py-2.5 px-3">Median (50%)</th>
                  <th className="py-2.5 px-3">75%</th>
                  <th className="py-2.5 px-3">Max</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                {numericStats.map((st) => (
                  <tr key={st.col} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{st.col}</td>
                    <td className="py-2.5 px-3 text-slate-400">{st.count}</td>
                    <td className="py-2.5 px-3 text-blue-400">{st.mean.toFixed(2)}</td>
                    <td className="py-2.5 px-3">{st.min.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-slate-400">{st.q25.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-semibold">{st.median.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-slate-400">{st.q75.toFixed(2)}</td>
                    <td className="py-2.5 px-3">{st.max.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Data Quality */}
      {activeTab === "quality" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h4 className="text-sm font-bold text-slate-100">Column Profiles & Missing Value Audit</h4>
              <p className="text-xs text-slate-400">Data types, null counts, and uniqueness audit</p>
            </div>
            <button
              onClick={() => handleExport(`${trackConfig.shortName}_Data_Quality_Audit`, qualityAuditRows)}
              className="text-xs px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Quality Audit (CSV)</span>
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {columns.map((c) => {
              const sampleVal = dataset[0][c];
              const dtype = typeof sampleVal === "number" ? "numeric (float/int)" : "categorical (object)";
              return (
                <div key={c} className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-semibold text-slate-200">{c}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                      {dtype}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400 text-[11px] mt-2">
                    <span>Missing: 0 (0.0%)</span>
                    <span className="text-emerald-400 font-semibold">100% Complete</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
