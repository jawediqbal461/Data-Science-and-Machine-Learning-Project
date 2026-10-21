import React, { useState } from "react";
import { useData } from "../../context/DataContext";
import { BENCHMARK_METRICS } from "../../data/capstoneData";
import { exportToCsv } from "../../utils/csvExport";
import { Cpu, Award, CheckCircle2, TrendingUp, Layers, Sliders, BarChart2, Download } from "lucide-react";

export const ModelEvaluationPage: React.FC = () => {
  const { activeTrack, trackConfig } = useData();
  const metrics = (BENCHMARK_METRICS as any)[activeTrack] || [];
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  const handleExportMetrics = () => {
    let exportRows = [];
    if (activeTrack === "SALES") {
      exportRows = metrics.map((m: any) => ({
        Track: activeTrack,
        Model_Name: m.model,
        R2_Score: m.r2,
        MAE_USD: m.mae,
        RMSE_USD: m.rmse,
        Generalization_Status: m.status
      }));
    } else {
      exportRows = metrics.map((m: any) => ({
        Track: activeTrack,
        Model_Name: m.model,
        Accuracy: m.accuracy,
        Precision: m.precision,
        Recall: m.recall,
        F1_Score: m.f1,
        ROC_AUC: m.roc,
        ...(m.cvF1 ? { Five_Fold_CV_F1: m.cvF1 } : {}),
        Generalization_Status: m.status
      }));
    }

    const success = exportToCsv(`${activeTrack}_Model_Benchmark_Metrics`, exportRows);
    if (success) {
      setExportNotice(`Exported ${exportRows.length} model benchmark rows to CSV!`);
      setTimeout(() => setExportNotice(null), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <span>Machine Learning Model Comparison & Pipeline Studio (§4 Phase 5)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Standardized scikit-learn Pipeline architecture fitted strictly on 80% train split (random_state=42)
          </p>
        </div>

        <button
          onClick={handleExportMetrics}
          className="text-xs px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1.5 shadow-sm transition-all active:scale-95 self-start sm:self-auto"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Metrics (CSV)</span>
        </button>
      </div>

      {exportNotice && (
        <div className="bg-emerald-950/80 border border-emerald-600 text-emerald-200 px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-lg animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{exportNotice}</span>
        </div>
      )}

      {/* Chosen Model Callout */}
      <div className="bg-gradient-to-r from-blue-950/60 to-slate-900 border border-blue-500/50 rounded-xl p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 mt-0.5">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-blue-400 font-semibold uppercase tracking-wider">
              Selected Production Pipeline
            </div>
            <h3 className="text-lg font-bold text-white mt-0.5">
              {trackConfig.bestModel}
            </h3>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Demonstrated optimal balance between bias and variance on held-out test evaluation.
              Saved to <code className="text-blue-300 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">models/final_pipeline.pkl</code> along with <code className="text-slate-300 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">models/model_metadata.json</code>.
            </p>
          </div>
        </div>

        <div className="flex flex-col items-end shrink-0">
          <span className="text-xs text-slate-400">Peak Validation Score</span>
          <span className="text-xl font-mono font-bold text-emerald-400">{trackConfig.benchmarkScore}</span>
          <span className="text-[10px] text-emerald-500/80 mt-0.5">Verified on Test Split</span>
        </div>
      </div>

      {/* Benchmark Metrics Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 bg-slate-950/60 border-b border-slate-800">
          <h3 className="text-sm font-bold text-slate-100">
            Held-Out Test Benchmark: Mandatory Evaluated Models
          </h3>
          <span className="text-xs text-slate-400">
            Stratified train/test split (80/20). Preprocessor fitted only on train fold to avoid target leakage.
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Estimator Algorithm</th>
                {activeTrack === "SALES" ? (
                  <>
                    <th className="py-3 px-4">R² Score</th>
                    <th className="py-3 px-4">MAE ($)</th>
                    <th className="py-3 px-4">RMSE ($)</th>
                  </>
                ) : (
                  <>
                    <th className="py-3 px-4">Accuracy</th>
                    <th className="py-3 px-4">Precision</th>
                    <th className="py-3 px-4">Recall</th>
                    <th className="py-3 px-4">F1-Score</th>
                    <th className="py-3 px-4">ROC-AUC</th>
                    {activeTrack === "HR_ATTRITION" && <th className="py-3 px-4">5-Fold CV F1</th>}
                  </>
                )}
                <th className="py-3 px-4">Generalization Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/60">
              {metrics.map((m: any, idx: number) => {
                const isBest = idx === 0;
                return (
                  <tr key={m.model} className={`hover:bg-slate-800/40 ${isBest ? "bg-blue-950/20" : ""}`}>
                    <td className="py-3 px-4 font-semibold text-slate-200 flex items-center gap-2">
                      {isBest && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />}
                      <span>{m.model}</span>
                    </td>
                    {activeTrack === "SALES" ? (
                      <>
                        <td className="py-3 px-4 font-mono font-bold text-emerald-400">{m.r2.toFixed(3)}</td>
                        <td className="py-3 px-4 font-mono text-slate-300">${m.mae.toFixed(2)}</td>
                        <td className="py-3 px-4 font-mono text-slate-400">${m.rmse.toFixed(2)}</td>
                      </>
                    ) : (
                      <>
                        <td className="py-3 px-4 font-mono text-slate-300">{(m.accuracy * 100).toFixed(1)}%</td>
                        <td className="py-3 px-4 font-mono text-slate-300">{(m.precision * 100).toFixed(1)}%</td>
                        <td className="py-3 px-4 font-mono text-sky-400 font-semibold">{(m.recall * 100).toFixed(1)}%</td>
                        <td className="py-3 px-4 font-mono font-bold text-emerald-400">{m.f1.toFixed(3)}</td>
                        <td className="py-3 px-4 font-mono text-purple-400">{m.roc.toFixed(3)}</td>
                        {activeTrack === "HR_ATTRITION" && (
                          <td className="py-3 px-4 font-mono text-amber-400 font-semibold">{m.cvF1.toFixed(3)}</td>
                        )}
                      </>
                    )}
                    <td className="py-3 px-4">
                      <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                        isBest
                          ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                          : "bg-slate-800 text-slate-400"
                      }`}>
                        {m.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pipeline Architecture Diagram */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2 mb-3">
          <Layers className="w-4 h-4 text-blue-400" />
          <span>Unified Production Pipeline Architecture (`joblib.dump`)</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Strictly encapsulated in a single scikit-learn Pipeline object to prevent transform drift during inference:
        </p>

        <div className="flex flex-col md:flex-row items-center gap-3 text-xs">
          {/* Step 1 */}
          <div className="flex-1 w-full bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-center">
            <span className="text-[10px] text-blue-400 font-mono block mb-1">STEP 1: PREPROCESSOR</span>
            <div className="font-semibold text-slate-200">ColumnTransformer</div>
            <div className="text-[11px] text-slate-400 mt-1">
              Numeric: Median Imputer + StandardScaler<br />
              Categorical: Mode Imputer + OneHotEncoder
            </div>
          </div>

          <span className="text-slate-600 font-bold">&rarr;</span>

          {/* Step 2 */}
          <div className="flex-1 w-full bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-center">
            <span className="text-[10px] text-emerald-400 font-mono block mb-1">STEP 2: ESTIMATOR</span>
            <div className="font-semibold text-slate-200">{trackConfig.bestModel}</div>
            <div className="text-[11px] text-slate-400 mt-1">
              Hyperparameters: max_depth, n_estimators tuned with random_state=42
            </div>
          </div>

          <span className="text-slate-600 font-bold">&rarr;</span>

          {/* Step 3 */}
          <div className="flex-1 w-full bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-center">
            <span className="text-[10px] text-purple-400 font-mono block mb-1">STEP 3: PERSISTENCE</span>
            <div className="font-semibold text-slate-200">models/final_pipeline.pkl</div>
            <div className="text-[11px] text-slate-400 mt-1">
              Accompanied by models/model_metadata.json
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
