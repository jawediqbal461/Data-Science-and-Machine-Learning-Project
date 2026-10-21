import React from "react";
import { SUBGROUP_EQUITY_DATA } from "../../data/capstoneData";
import { EthicalBanner } from "../EthicalBanner";
import { ShieldCheck, AlertTriangle, CheckCircle2, Scale, Users, Info } from "lucide-react";

export const ResponsibleMlPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Scale className="w-5 h-5 text-blue-400" />
          <span>Responsible ML & Subgroup Equity Review (§5 Mandatory)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Algorithmic fairness evaluation across demographic and operational cohorts. Flags small subgroups (n &lt; 30).
        </p>
      </div>

      {/* Mandatory Ethical Banner */}
      <EthicalBanner />

      {/* Equity Audit Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Demographic & Operational Subgroup Parity Audit</span>
            </h3>
            <span className="text-xs text-slate-400">
              Evaluates model Recall and False Positive Rate (FPR) parity across workforce slices
            </span>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-300 font-mono">
            Audit Standard: Disparate Impact Ratio &gt; 0.80
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Workforce Subgroup Category</th>
                <th className="py-3 px-4">Group Size (n)</th>
                <th className="py-3 px-4">Actual Attrition Rate</th>
                <th className="py-3 px-4">Predicted Attrition Rate</th>
                <th className="py-3 px-4">Model Recall</th>
                <th className="py-3 px-4">False Positive Rate (FPR)</th>
                <th className="py-3 px-4">Fairness Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/60 font-mono text-slate-300">
              {SUBGROUP_EQUITY_DATA.map((row) => {
                const isSmall = row.sampleSize < 30;
                return (
                  <tr key={row.group} className={`hover:bg-slate-800/40 ${isSmall ? "bg-amber-950/20" : ""}`}>
                    <td className="py-3 px-4 font-sans font-semibold text-slate-200">
                      {row.group}
                    </td>
                    <td className={`py-3 px-4 ${isSmall ? "text-amber-400 font-bold" : "text-slate-300"}`}>
                      {row.sampleSize}
                    </td>
                    <td className="py-3 px-4">{row.actualRate}</td>
                    <td className="py-3 px-4 text-slate-400">{row.predictedRate}</td>
                    <td className="py-3 px-4 text-emerald-400 font-bold">{row.recall}</td>
                    <td className="py-3 px-4 text-sky-400">{row.fpr}</td>
                    <td className="py-3 px-4 font-sans">
                      {isSmall ? (
                        <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-medium">
                          <AlertTriangle className="w-3 h-3 text-amber-400" />
                          Small Group (n &lt; 30)
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-medium">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          Balanced Parity
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Governance Explanations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 font-bold text-slate-200 mb-2">
            <Info className="w-4 h-4 text-blue-400" />
            <span>Why Audit Subgroup Disparities in Viva?</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Standard aggregate evaluation metrics (like 89% accuracy) can mask severe disparate impact where minority cohorts suffer high False Positive Rates.
            Demonstrating subgroup parity proves to the examiner that the model is safe for deployment without systemic bias.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 font-bold text-slate-200 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>The Small Sample Rule (n &lt; 30)</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Statistically, small groups (e.g. Executive Directors with n=18) lack sufficient sample support for reliable generalization.
            The pipeline explicitly flags these cohorts to mandate human qualitative review and disallow automated intervention.
          </p>
        </div>
      </div>
    </div>
  );
};
