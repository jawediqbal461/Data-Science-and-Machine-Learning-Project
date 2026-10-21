import React from "react";
import { ShieldAlert } from "lucide-react";

export const EthicalBanner: React.FC = () => {
  return (
    <div className="bg-amber-950/40 border border-amber-600/60 rounded-xl p-4 my-4 flex items-start gap-3 shadow-md">
      <ShieldAlert className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <h4 className="text-amber-300 font-semibold text-sm uppercase tracking-wider mb-1">
          Mandatory Ethical Workforce Governance Policy
        </h4>
        <p className="text-amber-100 text-sm leading-relaxed">
          This prediction is intended for workforce-level analysis and voluntary retention support.
          It must not be used as the sole basis for termination, promotion, salary, disciplinary, or hiring decisions.
        </p>
      </div>
    </div>
  );
};
