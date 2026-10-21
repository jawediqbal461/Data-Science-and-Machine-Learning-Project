import React, { useState } from "react";
import { useData } from "../../context/DataContext";
import { FEATURE_ENGINEERING_DATA, MISSING_VALUE_STRATEGIES } from "../../data/capstoneData";
import { exportToCsv } from "../../utils/csvExport";
import { Sliders, CheckCircle2, ShieldCheck, AlertCircle, Wrench, Download } from "lucide-react";

export const FeatureEngineeringPage: React.FC = () => {
  const { activeTrack, trackConfig } = useData();
  const features = FEATURE_ENGINEERING_DATA[activeTrack] || [];
  const [exportToast, setExportToast] = useState<string | null>(null);

  const handleExportFeatures = () => {
    const rows = features.map((f) => ({
      Track: activeTrack,
      Feature_Name: f.name,
      Mathematical_Formula: f.formula,
      Business_Domain_Meaning: f.meaning,
      Leakage_Safety_Audit: f.notes,
      Zero_Division_Guarded: "Yes (epsilon = 1e-6)"
    }));
    const success = exportToCsv(`${activeTrack}_Feature_Engineering_Catalog`, rows);
    if (success) {
      setExportToast(`Exported ${rows.length} engineered features to CSV!`);
      setTimeout(() => setExportToast(null), 3000);
    }
  };

  const handleExportImputation = () => {
    const rows = MISSING_VALUE_STRATEGIES.map((s) => ({
      Strategy_Name: s.strategy,
      F1_Score: s.f1,
      Recall: s.recall,
      Accuracy: s.accuracy,
      Retained_Data_Pct: s.retained,
      Evaluation_Notes: s.notes
    }));
    const success = exportToCsv("HR_Missing_Value_Imputation_Benchmark", rows);
    if (success) {
      setExportToast(`Exported ${rows.length} imputation benchmark strategies to CSV!`);
      setTimeout(() => setExportToast(null), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-400" />
            <span>Feature Engineering & Preprocessing Laboratory (§3 & §5)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Explicitly documented mathematical formulations, business domain rationale, and leakage safety certifications
          </p>
        </div>

        <button
          onClick={handleExportFeatures}
          className="text-xs px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1.5 shadow-sm transition-all active:scale-95 self-start sm:self-auto"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Features Catalog (CSV)</span>
        </button>
      </div>

      {exportToast && (
        <div className="bg-emerald-950/80 border border-emerald-600 text-emerald-200 px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-lg animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{exportToast}</span>
        </div>
      )}

      {/* Feature Engineering Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100">
              Engineered Domain Features ({features.length} Features)
            </h3>
            <span className="text-xs text-slate-400">
              Requirement: &ge;5 features for Sales/Churn, &ge;8 for HR Attrition
            </span>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Division-by-Zero Guarded
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Feature Name</th>
                <th className="py-3 px-4">Mathematical Formula</th>
                <th className="py-3 px-4">Business Domain Meaning</th>
                <th className="py-3 px-4">Leakage Safety Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/60">
              {features.map((f) => (
                <tr key={f.name} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-mono font-bold text-blue-400">
                    {f.name}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300 bg-slate-950/30">
                    {f.formula}
                  </td>
                  <td className="py-3 px-4 text-slate-300 leading-relaxed max-w-xs">
                    {f.meaning}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800">
                      <ShieldCheck className="w-3 h-3" /> {f.notes}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* HR Missing Value Strategy Laboratory per §5 */}
      {activeTrack === "HR_ATTRITION" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 bg-slate-950/60 border-b border-slate-800">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Wrench className="w-4 h-4 text-amber-400" />
              <span>HR Missing-Value Strategy Comparison Laboratory (§5 Mandatory)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparison across all four strategies (Row-Drop, Mean, Median, Mode) evaluated strictly on training folds.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Imputation Strategy</th>
                  <th className="py-3 px-4">F1-Score</th>
                  <th className="py-3 px-4">Recall</th>
                  <th className="py-3 px-4">Accuracy</th>
                  <th className="py-3 px-4">Retained Data</th>
                  <th className="py-3 px-4">Evaluation Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-900/60">
                {MISSING_VALUE_STRATEGIES.map((s, idx) => (
                  <tr
                    key={s.strategy}
                    className={`hover:bg-slate-800/40 ${
                      idx === 2 ? "bg-blue-950/20 border-l-4 border-l-blue-500" : ""
                    }`}
                  >
                    <td className="py-3 px-4 font-semibold text-slate-200">
                      {s.strategy}
                      {idx === 2 && (
                        <span className="ml-2 text-[10px] px-1.5 py-0.2 rounded bg-blue-900 text-blue-300 font-mono">
                          PIPELINE DEFAULT
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                      {s.f1.toFixed(3)}
                    </td>
                    <td className="py-3 px-4 font-mono text-sky-400">
                      {s.recall.toFixed(3)}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      {s.accuracy.toFixed(3)}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400">
                      {s.retained}
                    </td>
                    <td className="py-3 px-4 text-slate-400 max-w-sm">
                      {s.notes}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
