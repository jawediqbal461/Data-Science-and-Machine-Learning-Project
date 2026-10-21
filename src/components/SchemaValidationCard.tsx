import React, { useState } from "react";
import { useData } from "../context/DataContext";
import { CheckCircle2, AlertTriangle, XCircle, ArrowRightLeft, ShieldCheck, Lock, Upload, RotateCcw } from "lucide-react";

export const SchemaValidationCard: React.FC = () => {
  const {
    activeTrack,
    trackConfig,
    dataset,
    columnMappings,
    setColumnMappings,
    isMissingDataset,
    setIsMissingDataset,
    setIsUploadModalOpen,
    reloadBundled
  } = useData();

  const getExpectedColumns = () => {
    if (activeTrack === "SALES") {
      return ["Sales", "Quantity", "Discount", "Shipping_Cost", "Region", "Category", "Sub_Category"];
    } else if (activeTrack === "CHURN") {
      return ["Tenure_Months", "Contract_Type", "Monthly_Charges", "Total_Charges", "Support_Tickets", "Complaints"];
    } else {
      return ["Age", "Department", "Job_Role", "Monthly_Income", "Job_Level", "Years_At_Company", "Overtime", "Work_Life_Balance"];
    }
  };

  const expectedFeatures = getExpectedColumns();
  const targetCol = trackConfig.targetColumn;
  const allRequired = [...expectedFeatures, targetCol];

  const existingColumns = dataset.length > 0 ? Object.keys(dataset[0]) : [];

  const columnStatusList = allRequired.map((reqCol) => {
    const isTarget = reqCol === targetCol;
    const isDirectlyPresent = existingColumns.includes(reqCol);
    const mappedTo = columnMappings[reqCol];
    const isMappedPresent = mappedTo && existingColumns.includes(mappedTo);

    let status: "PRESENT" | "MAPPED" | "MISSING" = "MISSING";
    if (isDirectlyPresent) status = "PRESENT";
    else if (isMappedPresent) status = "MAPPED";

    return {
      column: reqCol,
      isRequired: true,
      isTarget,
      status,
      mappedTo
    };
  });

  const missingColumns = columnStatusList.filter((c) => c.status === "MISSING");
  const targetStatus = columnStatusList.find((c) => c.isTarget)?.status;
  const isTargetPresent = targetStatus === "PRESENT" || targetStatus === "MAPPED";
  const isValid = missingColumns.length === 0 && !isMissingDataset;
  const canTrainMl = isValid && isTargetPresent && dataset.length > 0;

  const handleMapChange = (reqCol: string, targetExistingCol: string) => {
    setColumnMappings((prev) => ({
      ...prev,
      [reqCol]: targetExistingCol
    }));
  };

  if (isMissingDataset || dataset.length === 0) {
    return (
      <div className="bg-rose-950/40 border border-rose-600/70 rounded-xl p-5 mb-6 shadow-md">
        <div className="flex items-center gap-3 text-rose-300 font-bold text-base mb-2">
          <XCircle className="w-6 h-6 text-rose-400 shrink-0" />
          <span>
            {isMissingDataset
              ? "SIMULATING MISSING_DATASET (Test Mode Active)"
              : "STOPPED AT VALIDATION GATE: NO DATASET LOADED"}
          </span>
        </div>
        <p className="text-rose-100 text-sm leading-relaxed mb-3">
          {isMissingDataset ? (
            <>
              Aapne top bar par <strong>&quot;Test Mode / Cold Start&quot;</strong> button click kiya hai jo jaan boojh kar dataset ko empty simulate karta hai taake zero-data error handling test ho sakay. Wapas normal data par janay ke liye neechay <strong>&quot;Restore Normal Dataset&quot;</strong> dabayein.
            </>
          ) : (
            <>
              No dataset loaded. Per assignment non-negotiables: analysis and ML training are strictly locked.
              Upload a manual file or reload bundled dataset to proceed.
            </>
          )}
        </p>

        <div className="flex flex-wrap items-center gap-2.5 mb-3">
          {/* Quick exit simulation / restore button */}
          <button
            onClick={() => {
              setIsMissingDataset(false);
              reloadBundled();
            }}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-2 shadow-sm transition-all cursor-pointer ring-1 ring-emerald-400/40"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Restore Normal Dataset (Exit Test Mode)</span>
          </button>

          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 shadow-sm transition-all cursor-pointer"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Manual Dataset</span>
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-rose-300 bg-rose-900/40 px-3 py-1.5 rounded-lg border border-rose-700/50">
          <Lock className="w-3.5 h-3.5 text-rose-400" />
          <span>Downstream EDA, Cross-Validation, and Inference Engines: LOCKED while dataset is missing</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`rounded-xl border p-5 mb-6 shadow-sm transition-all ${
      isValid
        ? "bg-slate-900/90 border-slate-800"
        : "bg-amber-950/30 border-amber-600/60"
    }`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2.5">
          {isValid ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          )}
          <div>
            <h3 className="font-bold text-slate-100 text-sm sm:text-base flex items-center gap-2">
              Schema Validation Gate (§2.6)
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded ${
                isValid
                  ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                  : "bg-amber-950 text-amber-300 border border-amber-800"
              }`}>
                {isValid ? "PASSED ✅" : "ATTENTION REQUIRED ⚠️"}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Target Column: <code className="text-blue-400 font-bold">{targetCol}</code> ({isTargetPresent ? "Detected" : "MISSING"})
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="text-xs font-mono px-3 py-1 rounded bg-slate-950 border border-slate-800 text-slate-300">
            ML Training Gate: {canTrainMl ? (
              <span className="text-emerald-400 font-bold">UNLOCKED 🟢</span>
            ) : (
              <span className="text-rose-400 font-bold">LOCKED 🔒</span>
            )}
          </div>
        </div>
      </div>

      {/* Column Schema Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border border-slate-800 rounded-lg overflow-hidden">
          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2 px-3">Canonical Concept</th>
              <th className="py-2 px-3">Type</th>
              <th className="py-2 px-3">Status</th>
              <th className="py-2 px-3">Mapped Column</th>
              <th className="py-2 px-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-slate-900/60">
            {columnStatusList.map((item) => (
              <tr key={item.column} className="hover:bg-slate-800/40">
                <td className="py-2 px-3 font-mono font-medium text-slate-200">
                  {item.column}
                  {item.isTarget && (
                    <span className="ml-1.5 px-1.5 py-0.2 rounded text-[10px] bg-blue-900/60 text-blue-300 border border-blue-700">
                      TARGET
                    </span>
                  )}
                </td>
                <td className="py-2 px-3 text-slate-400">Required Predictor</td>
                <td className="py-2 px-3">
                  {item.status === "PRESENT" && (
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 font-semibold">
                      PRESENT
                    </span>
                  )}
                  {item.status === "MAPPED" && (
                    <span className="px-2 py-0.5 rounded text-[10px] bg-sky-950 text-sky-300 border border-sky-800 font-semibold">
                      MAPPED
                    </span>
                  )}
                  {item.status === "MISSING" && (
                    <span className="px-2 py-0.5 rounded text-[10px] bg-rose-950 text-rose-300 border border-rose-800 font-semibold">
                      MISSING
                    </span>
                  )}
                </td>
                <td className="py-2 px-3 font-mono text-slate-300">
                  {item.status === "MAPPED" ? item.mappedTo : item.status === "PRESENT" ? item.column : "-"}
                </td>
                <td className="py-2 px-3">
                  {item.status === "MISSING" ? (
                    <select
                      className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs focus:ring-1 focus:ring-blue-500"
                      onChange={(e) => handleMapChange(item.column, e.target.value)}
                      defaultValue=""
                    >
                      <option value="" disabled>-- Map to existing column --</option>
                      {existingColumns.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  ) : (
                    <span className="text-slate-500 text-[11px]">Aligned</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {!isTargetPresent && (
        <div className="mt-3 p-2.5 rounded bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
          <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>
            CRITICAL: Target column <code>{targetCol}</code> is not present in the current dataset.
            Machine learning training and inference are disabled until this field is provided or mapped.
          </span>
        </div>
      )}
    </div>
  );
};
