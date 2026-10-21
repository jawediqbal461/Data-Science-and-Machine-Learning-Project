import React, { useState, useRef } from "react";
import { useData } from "../context/DataContext";
import {
  Upload,
  X,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  Filter,
  Wrench,
  Download,
  Info,
  Layers,
  Database
} from "lucide-react";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose }) => {
  const {
    activeTrack,
    setActiveTrack,
    handleFileUpload,
    setActivePage,
    setIsMissingDataset
  } = useData();

  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [parsedRows, setParsedRows] = useState<any[]>([]);
  const [selectedTrack, setSelectedTrack] = useState<"SALES" | "CHURN" | "HR_ATTRITION">(activeTrack);
  const [cleaningLog, setCleaningLog] = useState<string[]>([]);
  const [parseError, setParseError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  // Robust CSV parser supporting quotes and commas
  const parseCSVContent = (text: string): { rows: any[]; error?: string } => {
    try {
      const lines = text
        .split(/\r\n|\n/)
        .map((l) => l.trim())
        .filter((l) => l.length > 0);

      if (lines.length < 2) {
        return { rows: [], error: "CSV file must contain a header row and at least 1 data row." };
      }

      // Parse line into cells respecting quotes
      const parseLine = (line: string): string[] => {
        const cells: string[] = [];
        let cur = "";
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          if (char === '"' || char === "'") {
            inQuotes = !inQuotes;
          } else if ((char === "," || char === "\t") && !inQuotes) {
            cells.push(cur.trim().replace(/^["']|["']$/g, ""));
            cur = "";
          } else {
            cur += char;
          }
        }
        cells.push(cur.trim().replace(/^["']|["']$/g, ""));
        return cells;
      };

      const headers = parseLine(lines[0]);
      if (headers.length === 0) {
        return { rows: [], error: "No columns detected in the first line." };
      }

      const rows: any[] = [];
      for (let i = 1; i < lines.length; i++) {
        const vals = parseLine(lines[i]);
        const row: Record<string, any> = {};
        headers.forEach((h, idx) => {
          const val = vals[idx] !== undefined ? vals[idx] : "";
          const num = Number(val);
          row[h] = val !== "" && !isNaN(num) ? num : val;
        });
        rows.push(row);
      }

      return { rows };
    } catch (err: any) {
      return { rows: [], error: `Failed to parse file: ${err.message}` };
    }
  };

  const handleFile = (file: File) => {
    setParseError(null);
    setCleaningLog([]);
    setFileName(file.name);

    // Auto-detect track if filename gives hints
    const lowerName = file.name.toLowerCase();
    if (lowerName.includes("sale") || lowerName.includes("superstore") || lowerName.includes("retail")) {
      setSelectedTrack("SALES");
    } else if (lowerName.includes("churn") || lowerName.includes("telco") || lowerName.includes("customer")) {
      setSelectedTrack("CHURN");
    } else if (lowerName.includes("hr") || lowerName.includes("attrition") || lowerName.includes("employee")) {
      setSelectedTrack("HR_ATTRITION");
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      if (!text) {
        setParseError("The uploaded file was empty.");
        return;
      }
      const result = parseCSVContent(text);
      if (result.error) {
        setParseError(result.error);
        setParsedRows([]);
      } else {
        setParsedRows(result.rows);
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  // Sample templates generator
  const loadSampleDataset = (track: "SALES" | "CHURN" | "HR_ATTRITION") => {
    setSelectedTrack(track);
    setCleaningLog([]);
    setParseError(null);

    let sampleData: any[] = [];
    let name = "";

    if (track === "SALES") {
      name = "Sample_Superstore_Sales_Data.csv";
      sampleData = [
        { Order_ID: "CA-2026-1001", Customer_Name: "TechCorp Global", Segment: "Corporate", Region: "West", Category: "Technology", Sub_Category: "Phones", Sales: 899.99, Quantity: 3, Discount: 0.1, Profit: 245.5, Returned: "No" },
        { Order_ID: "CA-2026-1002", Customer_Name: "Alina Khan", Segment: "Consumer", Region: "East", Category: "Furniture", Sub_Category: "Chairs", Sales: 420.0, Quantity: 2, Discount: 0.2, Profit: -35.2, Returned: "No" },
        { Order_ID: "CA-2026-1003", Customer_Name: "Apex Logistics", Segment: "Home Office", Region: "Central", Category: "Office Supplies", Sub_Category: "Storage", Sales: 185.5, Quantity: 5, Discount: 0.05, Profit: 42.1, Returned: "No" },
        { Order_ID: "CA-2026-1004", Customer_Name: "David Miller", Segment: "Consumer", Region: "South", Category: "Technology", Sub_Category: "Accessories", Sales: 129.9, Quantity: 4, Discount: 0.0, Profit: 51.4, Returned: "Yes" },
        { Order_ID: "CA-2026-1005", Customer_Name: "Zenith Retailers", Segment: "Corporate", Region: "West", Category: "Furniture", Sub_Category: "Tables", Sales: 950.0, Quantity: 1, Discount: 0.3, Profit: -120.0, Returned: "No" },
        { Order_ID: "CA-2026-1006", Customer_Name: "Farhan Saeed", Segment: "Consumer", Region: "East", Category: "Office Supplies", Sub_Category: "Paper", Sales: 45.0, Quantity: 6, Discount: 0.0, Profit: 18.5, Returned: "No" },
        { Order_ID: "CA-2026-1007", Customer_Name: "Global Trade Inc", Segment: "Corporate", Region: "Central", Category: "Technology", Sub_Category: "Copiers", Sales: 1650.0, Quantity: 2, Discount: 0.15, Profit: 490.0, Returned: "No" },
        { Order_ID: "CA-2026-1008", Customer_Name: "Sara Ahmed", Segment: "Home Office", Region: "West", Category: "Furniture", Sub_Category: "Bookcases", Sales: 310.0, Quantity: 2, Discount: 0.25, Profit: -15.8, Returned: "No" }
      ];
    } else if (track === "CHURN") {
      name = "Sample_Customer_Churn_Data.csv";
      sampleData = [
        { Customer_ID: "CUST-901", Age: 34, Gender: "Female", Tenure_Months: 4, Contract_Type: "Month-to-month", Monthly_Charges: 78.5, Total_Charges: 314.0, Tech_Support: "No", Support_Tickets: 5, Complaints: 3, Satisfaction_Score: 2, Churned: 1 },
        { Customer_ID: "CUST-902", Age: 52, Gender: "Male", Tenure_Months: 36, Contract_Type: "Two year", Monthly_Charges: 95.0, Total_Charges: 3420.0, Tech_Support: "Yes", Support_Tickets: 1, Complaints: 0, Satisfaction_Score: 5, Churned: 0 },
        { Customer_ID: "CUST-903", Age: 27, Gender: "Female", Tenure_Months: 8, Contract_Type: "Month-to-month", Monthly_Charges: 64.2, Total_Charges: 513.6, Tech_Support: "No", Support_Tickets: 3, Complaints: 2, Satisfaction_Score: 2, Churned: 1 },
        { Customer_ID: "CUST-904", Age: 45, Gender: "Male", Tenure_Months: 24, Contract_Type: "One year", Monthly_Charges: 82.0, Total_Charges: 1968.0, Tech_Support: "Yes", Support_Tickets: 0, Complaints: 0, Satisfaction_Score: 4, Churned: 0 },
        { Customer_ID: "CUST-905", Age: 29, Gender: "Male", Tenure_Months: 2, Contract_Type: "Month-to-month", Monthly_Charges: 89.9, Total_Charges: 179.8, Tech_Support: "No", Support_Tickets: 6, Complaints: 4, Satisfaction_Score: 1, Churned: 1 },
        { Customer_ID: "CUST-906", Age: 61, Gender: "Female", Tenure_Months: 48, Contract_Type: "Two year", Monthly_Charges: 104.5, Total_Charges: 5016.0, Tech_Support: "Yes", Support_Tickets: 1, Complaints: 0, Satisfaction_Score: 5, Churned: 0 }
      ];
    } else {
      name = "Sample_IBM_HR_Attrition_Data.csv";
      sampleData = [
        { Employee_ID: "EMP-101", Age: 31, Department: "Sales", Job_Role: "Sales Executive", Monthly_Income: 5200, Overtime: "Yes", Years_At_Company: 2, Job_Satisfaction: 2, Work_Life_Balance: 1, Distance_From_Home: 22, Attrition: "Yes" },
        { Employee_ID: "EMP-102", Age: 42, Department: "Research & Development", Job_Role: "Research Scientist", Monthly_Income: 7800, Overtime: "No", Years_At_Company: 8, Job_Satisfaction: 4, Work_Life_Balance: 3, Distance_From_Home: 5, Attrition: "No" },
        { Employee_ID: "EMP-103", Age: 26, Department: "Research & Development", Job_Role: "Laboratory Technician", Monthly_Income: 3100, Overtime: "Yes", Years_At_Company: 1, Job_Satisfaction: 1, Work_Life_Balance: 2, Distance_From_Home: 18, Attrition: "Yes" },
        { Employee_ID: "EMP-104", Age: 49, Department: "Sales", Job_Role: "Manager", Monthly_Income: 12500, Overtime: "No", Years_At_Company: 14, Job_Satisfaction: 4, Work_Life_Balance: 4, Distance_From_Home: 3, Attrition: "No" },
        { Employee_ID: "EMP-105", Age: 36, Department: "Human Resources", Job_Role: "HR Specialist", Monthly_Income: 4800, Overtime: "No", Years_At_Company: 5, Job_Satisfaction: 3, Work_Life_Balance: 3, Distance_From_Home: 8, Attrition: "No" },
        { Employee_ID: "EMP-106", Age: 28, Department: "Sales", Job_Role: "Sales Representative", Monthly_Income: 2900, Overtime: "Yes", Years_At_Company: 1, Job_Satisfaction: 2, Work_Life_Balance: 1, Distance_From_Home: 25, Attrition: "Yes" }
      ];
    }

    setFileName(name);
    setParsedRows(sampleData);
  };

  // Cleaning action: Remove duplicates
  const cleanRemoveDuplicates = () => {
    if (parsedRows.length === 0) return;
    const seen = new Set();
    const unique: any[] = [];
    let dupsCount = 0;

    parsedRows.forEach((r) => {
      const serialized = JSON.stringify(r);
      if (!seen.has(serialized)) {
        seen.add(serialized);
        unique.push(r);
      } else {
        dupsCount++;
      }
    });

    setParsedRows(unique);
    setCleaningLog((prev) => [
      ...prev,
      dupsCount > 0
        ? `✅ Removed ${dupsCount} duplicate row(s).`
        : `ℹ️ No duplicate rows detected.`
    ]);
  };

  // Cleaning action: Impute missing numericals with median
  const cleanImputeNumerics = () => {
    if (parsedRows.length === 0) return;
    const cols = Object.keys(parsedRows[0]);
    let fixedCount = 0;

    const cleaned = parsedRows.map((r) => ({ ...r }));

    cols.forEach((col) => {
      const numVals = cleaned
        .map((r) => r[col])
        .filter((v) => typeof v === "number" && !isNaN(v));

      if (numVals.length > 0) {
        numVals.sort((a, b) => a - b);
        const median = numVals[Math.floor(numVals.length / 2)];

        cleaned.forEach((r) => {
          if (r[col] === null || r[col] === undefined || r[col] === "" || isNaN(r[col])) {
            r[col] = median;
            fixedCount++;
          }
        });
      }
    });

    setParsedRows(cleaned);
    setCleaningLog((prev) => [
      ...prev,
      fixedCount > 0
        ? `✅ Imputed ${fixedCount} missing numeric cell(s) with column median.`
        : `ℹ️ All numeric columns were already complete.`
    ]);
  };

  // Cleaning action: Fill missing text values
  const cleanFillText = () => {
    if (parsedRows.length === 0) return;
    const cols = Object.keys(parsedRows[0]);
    let fixedCount = 0;

    const cleaned = parsedRows.map((r) => {
      const row = { ...r };
      cols.forEach((col) => {
        if (row[col] === null || row[col] === undefined || row[col] === "") {
          row[col] = "Unknown";
          fixedCount++;
        }
      });
      return row;
    });

    setParsedRows(cleaned);
    setCleaningLog((prev) => [
      ...prev,
      fixedCount > 0
        ? `✅ Replaced ${fixedCount} blank/null categorical cell(s) with "Unknown".`
        : `ℹ️ No blank categorical values found.`
    ]);
  };

  // Cleaning action: Trim whitespace
  const cleanTrimWhitespace = () => {
    if (parsedRows.length === 0) return;
    const cols = Object.keys(parsedRows[0]);
    let trimmedCount = 0;

    const cleaned = parsedRows.map((r) => {
      const row = { ...r };
      cols.forEach((c) => {
        if (typeof row[c] === "string") {
          const original = row[c];
          row[c] = original.trim();
          if (row[c] !== original) trimmedCount++;
        }
      });
      return row;
    });

    setParsedRows(cleaned);
    setCleaningLog((prev) => [
      ...prev,
      trimmedCount > 0
        ? `✅ Trimmed whitespace on ${trimmedCount} cell(s).`
        : `ℹ️ All text cells are already trimmed.`
    ]);
  };

  // Apply to app context
  const handleApply = (targetPage: string = "explorer") => {
    if (parsedRows.length === 0) return;

    setActiveTrack(selectedTrack);
    setIsMissingDataset(false);
    handleFileUpload(fileName || "custom_uploaded_dataset.csv", parsedRows);
    setActivePage(targetPage);
    onClose();
  };

  const columns = parsedRows.length > 0 ? Object.keys(parsedRows[0]) : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-slate-100 flex items-center gap-2">
                <span>Upload & Clean Manual Dataset</span>
                <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-blue-900/40 text-blue-300 border border-blue-700">
                  CSV / Excel Support
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Upload Sales data, Customer Churn, HR Attrition, or custom CSV to clean, analyze, and generate reports
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-5 custom-scrollbar flex-1">
          {/* Track Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
              1. Select Domain Track for this Dataset:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {[
                { id: "SALES", title: "Sales & Profitability", desc: "Superstore / Retail sales records", icon: "📊" },
                { id: "CHURN", title: "Customer Churn", desc: "Telco / SaaS churn & retention", icon: "👥" },
                { id: "HR_ATTRITION", title: "HR Attrition", desc: "IBM employee retention & factors", icon: "🏢" }
              ].map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setSelectedTrack(t.id as any)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    selectedTrack === t.id
                      ? "bg-blue-600/15 border-blue-500 text-blue-100 shadow-sm"
                      : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{t.icon}</span>
                    <span className="text-xs font-bold text-slate-200">{t.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{t.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Quick Pre-made Template Loader */}
          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
              <div>
                <div className="text-xs font-semibold text-slate-200">
                  Don't have a CSV file on hand?
                </div>
                <div className="text-[11px] text-slate-400">
                  Load a verified realistic sample dataset with 1 click to test cleaning and reporting:
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5 shrink-0">
              <button
                onClick={() => loadSampleDataset("SALES")}
                className="text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-blue-300 border border-slate-700 font-medium transition-colors"
              >
                + Sales Data
              </button>
              <button
                onClick={() => loadSampleDataset("CHURN")}
                className="text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-purple-300 border border-slate-700 font-medium transition-colors"
              >
                + Churn Data
              </button>
              <button
                onClick={() => loadSampleDataset("HR_ATTRITION")}
                className="text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-slate-700 font-medium transition-colors"
              >
                + HR Attrition Data
              </button>
            </div>
          </div>

          {/* Drag & Drop Upload Zone */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
              2. Upload Your CSV or Excel File:
            </label>
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
                dragActive
                  ? "border-blue-400 bg-blue-950/20"
                  : fileName
                  ? "border-emerald-500/50 bg-emerald-950/10"
                  : "border-slate-700 hover:border-slate-500 bg-slate-950/40"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls,.tsv,.txt"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFile(e.target.files[0]);
                }}
              />
              <div className="flex flex-col items-center justify-center gap-2">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    fileName
                      ? "bg-emerald-500/20 text-emerald-400"
                      : "bg-blue-600/10 text-blue-400"
                  }`}
                >
                  {fileName ? <CheckCircle2 className="w-6 h-6" /> : <Upload className="w-6 h-6" />}
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-200">
                    {fileName ? (
                      <span className="text-emerald-300 font-mono">{fileName}</span>
                    ) : (
                      "Click to browse file or Drag & Drop here"
                    )}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Accepts standard CSV with comma/tab delimiters (.csv, .xlsx, .tsv)
                  </div>
                </div>
              </div>
            </div>

            {parseError && (
              <div className="mt-2.5 p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{parseError}</span>
              </div>
            )}
          </div>

          {/* Quick Data Cleaning Tools (When Data is Loaded) */}
          {parsedRows.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                    3. Data Cleaning & Preparation Actions:
                  </span>
                </div>
                <div className="text-xs text-slate-400">
                  <span className="text-emerald-400 font-bold">{parsedRows.length}</span> rows loaded •{" "}
                  <span className="text-blue-400 font-bold">{columns.length}</span> columns
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <button
                  type="button"
                  onClick={cleanRemoveDuplicates}
                  className="px-2.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Filter className="w-3.5 h-3.5 text-blue-400" />
                  <span>Drop Duplicates</span>
                </button>
                <button
                  type="button"
                  onClick={cleanImputeNumerics}
                  className="px-2.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Impute Numbers</span>
                </button>
                <button
                  type="button"
                  onClick={cleanFillText}
                  className="px-2.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Fill Categorical</span>
                </button>
                <button
                  type="button"
                  onClick={cleanTrimWhitespace}
                  className="px-2.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Wrench className="w-3.5 h-3.5 text-purple-400" />
                  <span>Trim Spaces</span>
                </button>
              </div>

              {cleaningLog.length > 0 && (
                <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs space-y-1">
                  {cleaningLog.map((log, i) => (
                    <div key={i} className="text-slate-300 font-mono text-[11px]">
                      {log}
                    </div>
                  ))}
                </div>
              )}

              {/* Data Preview */}
              <div>
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Live Preview (First 5 Rows):
                </div>
                <div className="overflow-x-auto rounded-lg border border-slate-800 max-h-48 custom-scrollbar">
                  <table className="w-full text-left text-[11px] font-mono border-collapse">
                    <thead className="bg-slate-900 text-slate-300 sticky top-0">
                      <tr>
                        {columns.slice(0, 8).map((col) => (
                          <th key={col} className="p-2 border-b border-slate-800 whitespace-nowrap">
                            {col}
                          </th>
                        ))}
                        {columns.length > 8 && (
                          <th className="p-2 border-b border-slate-800 text-slate-500 whitespace-nowrap">
                            +{columns.length - 8} more cols
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950">
                      {parsedRows.slice(0, 5).map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-900/50">
                          {columns.slice(0, 8).map((col) => (
                            <td key={col} className="p-2 text-slate-300 whitespace-nowrap">
                              {String(row[col] ?? "null")}
                            </td>
                          ))}
                          {columns.length > 8 && (
                            <td className="p-2 text-slate-500">...</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 sm:p-5 border-t border-slate-800 bg-slate-900/90 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-slate-400">
            {parsedRows.length > 0 ? (
              <span>
                Ready to analyze: <strong className="text-slate-200">{parsedRows.length}</strong> records under{" "}
                <strong className="text-blue-400">{selectedTrack}</strong>
              </span>
            ) : (
              <span>Select or upload a file above to begin</span>
            )}
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 sm:flex-none px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={parsedRows.length === 0}
              onClick={() => handleApply("explorer")}
              className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold shadow-md shadow-blue-600/30 flex items-center justify-center gap-1.5 transition-all"
            >
              <span>Apply & Open Data Explorer</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              type="button"
              disabled={parsedRows.length === 0}
              onClick={() => handleApply("recommendations")}
              className="hidden md:flex px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold shadow-md shadow-emerald-600/30 items-center justify-center gap-1.5 transition-all"
            >
              <span>Apply & Check Report</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
