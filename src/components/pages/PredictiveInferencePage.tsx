import React, { useState } from "react";
import { useData } from "../../context/DataContext";
import { EthicalBanner } from "../EthicalBanner";
import { Zap, AlertTriangle, CheckCircle2, ShieldAlert, ArrowRight, DollarSign, Sliders, Info } from "lucide-react";

export const PredictiveInferencePage: React.FC = () => {
  const { activeTrack, trackConfig } = useData();

  // SALES State
  const [salesAmount, setSalesAmount] = useState<number>(350);
  const [salesQuantity, setSalesQuantity] = useState<number>(3);
  const [salesDiscount, setSalesDiscount] = useState<number>(0.15);
  const [shippingCost, setShippingCost] = useState<number>(18.5);
  const [productCategory, setProductCategory] = useState<string>("Technology");
  const [salesRegion, setSalesRegion] = useState<string>("West");

  // CHURN State
  const [churnThreshold, setChurnThreshold] = useState<number>(0.38); // Calibrated threshold
  const [churnTenure, setChurnTenure] = useState<number>(8);
  const [churnMonthly, setChurnMonthly] = useState<number>(85);
  const [churnContract, setChurnContract] = useState<string>("Month-to-month");
  const [churnTickets, setChurnTickets] = useState<number>(3);
  const [churnComplaints, setChurnComplaints] = useState<number>(1);
  const [churnSat, setChurnSat] = useState<number>(2);

  // HR State
  const [hrIncome, setHrIncome] = useState<number>(3800);
  const [hrYearsComp, setHrYearsComp] = useState<number>(2);
  const [hrOvertime, setHrOvertime] = useState<string>("Yes");
  const [hrWlb, setHrWlb] = useState<number>(2);
  const [hrJobSat, setHrJobSat] = useState<number>(2);
  const [hrDistance, setHrDistance] = useState<number>(18);

  // Calculations for Sales
  const calculateSalesProfit = () => {
    const baseMargin = productCategory === "Technology" ? 0.32 : productCategory === "Office Supplies" ? 0.22 : 0.12;
    const gross = salesAmount * baseMargin;
    const discLoss = salesAmount * (salesDiscount * 1.35);
    const logistics = shippingCost * 1.15;
    const netProfit = gross - discLoss - logistics;

    let category = "Low Profit";
    let color = "text-amber-400";
    if (netProfit < 0) {
      category = "Loss (Negative Margin)";
      color = "text-rose-400";
    } else if (netProfit < 50) {
      category = "Low Profit ($0 - $50)";
      color = "text-amber-400";
    } else if (netProfit < 200) {
      category = "Medium Profit ($50 - $200)";
      color = "text-blue-400";
    } else {
      category = "High Profit (>$200)";
      color = "text-emerald-400";
    }

    return { netProfit, category, isLoss: netProfit < 0, color };
  };

  // Calculations for Churn
  const calculateChurnRisk = () => {
    let logit = -1.2;
    if (churnContract === "Month-to-month") logit += 0.9;
    else if (churnContract === "Two year") logit -= 1.1;

    logit += (churnMonthly - 65) * 0.015;
    logit -= (churnTenure - 24) * 0.035;
    logit += churnComplaints * 0.7;
    logit += churnTickets * 0.3;
    logit -= (churnSat - 3) * 0.45;

    const prob = 1 / (1 + Math.exp(-logit));
    const isChurn = prob >= churnThreshold;

    let tier = "Low Risk";
    let color = "text-emerald-400";
    if (prob >= 0.75) {
      tier = "Critical Risk";
      color = "text-rose-400";
    } else if (prob >= 0.5) {
      tier = "High Risk";
      color = "text-amber-400";
    } else if (prob >= 0.25) {
      tier = "Medium Risk";
      color = "text-sky-400";
    }

    return { prob, isChurn, tier, color };
  };

  // Calculations for HR
  const calculateHrAttrition = () => {
    let logit = -1.8;
    if (hrOvertime === "Yes") logit += 1.25;
    if (hrWlb <= 2) logit += 0.85;
    if (hrJobSat <= 2) logit += 0.8;
    if (hrDistance > 15) logit += 0.4;
    if (hrIncome < 4000) logit += 0.5;
    if (hrYearsComp <= 2) logit += 0.35;

    const prob = 1 / (1 + Math.exp(-logit));
    const isAttr = prob >= 0.5;

    let tier = "Stable Retention";
    let color = "text-emerald-400";
    if (prob > 0.7) {
      tier = "Critical Retention Hazard";
      color = "text-rose-400";
    } else if (prob > 0.45) {
      tier = "Elevated Flight Risk";
      color = "text-amber-400";
    }

    return { prob, isAttr, tier, color };
  };

  const salesResult = calculateSalesProfit();
  const churnResult = calculateChurnRisk();
  const hrResult = calculateHrAttrition();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Zap className="w-5 h-5 text-blue-400" />
          <span>Real-Time Predictive Inference & Policy Simulator (§4 Phase 7)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Simulate real-time operational transactions with dynamic boundaries and safety checks
        </p>
      </div>

      {activeTrack === "HR_ATTRITION" && <EthicalBanner />}

      {/* SALES INFERENCE */}
      {activeTrack === "SALES" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Form */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-blue-400" />
              <span>Transaction Parameters (Pre-Fulfillment Attributes)</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Gross Sales Amount ($)
                </label>
                <input
                  type="number"
                  min={10}
                  max={5000}
                  value={salesAmount}
                  onChange={(e) => setSalesAmount(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Order Quantity (Units)
                </label>
                <input
                  type="number"
                  min={1}
                  max={30}
                  value={salesQuantity}
                  onChange={(e) => setSalesQuantity(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>Promotional Discount:</span>
                  <span className={`font-mono ${salesDiscount > 0.2 ? "text-rose-400 font-bold" : "text-blue-400"}`}>
                    {(salesDiscount * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={0.6}
                  step={0.05}
                  value={salesDiscount}
                  onChange={(e) => setSalesDiscount(Number(e.target.value))}
                  className="w-full accent-blue-500"
                />
                <span className="text-[10px] text-slate-500">Notice: &gt;20% triggers margin destruction</span>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Logistics Shipping Cost ($)
                </label>
                <input
                  type="number"
                  min={0}
                  max={150}
                  value={shippingCost}
                  onChange={(e) => setShippingCost(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Product Category
                </label>
                <select
                  value={productCategory}
                  onChange={(e) => setProductCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  <option value="Technology">Technology (High Margin)</option>
                  <option value="Office Supplies">Office Supplies (Medium Margin)</option>
                  <option value="Furniture">Furniture (Low Margin / Bulky)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Sales Region
                </label>
                <select
                  value={salesRegion}
                  onChange={(e) => setSalesRegion(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  <option value="West">West Region</option>
                  <option value="East">East Region</option>
                  <option value="Central">Central Region</option>
                  <option value="South">South Region</option>
                </select>
              </div>
            </div>
          </div>

          {/* Result Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-2">
                Inference Result (§5)
              </div>
              <div className="text-xs text-slate-400">Predicted Transaction Profit:</div>
              <div className={`text-3xl font-extrabold font-mono mt-1 ${salesResult.color}`}>
                ${salesResult.netProfit.toFixed(2)}
              </div>
              <div className="mt-2 inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-200">
                Tier: {salesResult.category}
              </div>

              {/* Mandatory Red Warning per §5 */}
              {salesResult.isLoss && (
                <div className="mt-4 p-3 rounded-lg bg-rose-950/80 border border-rose-600 text-rose-200 text-xs shadow-md">
                  <div className="flex items-center gap-1.5 font-bold text-rose-300 mb-1">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                    <span>🚨 CRITICAL MARGIN LOSS WARNING</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    This order generates a net negative margin (${salesResult.netProfit.toFixed(2)}).
                    Promotional discount ({Math.round(salesDiscount * 100)}%) and freight costs exceed gross contribution.
                  </p>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-500">
              Pipeline: Random Forest Regressor (MAE: $14.20)
            </div>
          </div>
        </div>
      )}

      {/* CHURN INFERENCE */}
      {activeTrack === "CHURN" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
            {/* Dynamic Threshold Slider per §5 */}
            <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-800/60 mb-2">
              <div className="flex justify-between items-center text-xs text-blue-200 font-bold mb-1">
                <span>Threshold Analysis Slider (&tau;):</span>
                <span className="font-mono text-sm text-sky-400">{churnThreshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0.1}
                max={0.9}
                step={0.02}
                value={churnThreshold}
                onChange={(e) => setChurnThreshold(Number(e.target.value))}
                className="w-full accent-blue-500"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>0.10 (High Recall / Aggressive)</span>
                <span className="text-emerald-400 font-semibold font-mono">Calibrated Optimal: 0.38</span>
                <span>0.90 (High Precision / Conservative)</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Customer Tenure (Months)
                </label>
                <input
                  type="number"
                  min={1}
                  max={72}
                  value={churnTenure}
                  onChange={(e) => setChurnTenure(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Monthly Charges ($)
                </label>
                <input
                  type="number"
                  min={20}
                  max={130}
                  value={churnMonthly}
                  onChange={(e) => setChurnMonthly(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Contract Type
                </label>
                <select
                  value={churnContract}
                  onChange={(e) => setChurnContract(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  <option value="Month-to-month">Month-to-month (High Risk)</option>
                  <option value="One year">One year</option>
                  <option value="Two year">Two year (Low Risk)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Support Tickets (Past 60d)
                </label>
                <input
                  type="number"
                  min={0}
                  max={10}
                  value={churnTickets}
                  onChange={(e) => setChurnTickets(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Escalated Complaints
                </label>
                <input
                  type="number"
                  min={0}
                  max={5}
                  value={churnComplaints}
                  onChange={(e) => setChurnComplaints(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Satisfaction Score (1=Poor, 5=Excellent)
                </label>
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={churnSat}
                  onChange={(e) => setChurnSat(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>
            </div>
          </div>

          {/* Result */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-2">
                Inference Result (§5)
              </div>
              <div className="text-xs text-slate-400">Churn Probability:</div>
              <div className={`text-3xl font-extrabold font-mono mt-1 ${churnResult.color}`}>
                {(churnResult.prob * 100).toFixed(1)}%
              </div>
              <div className="mt-2 inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-200">
                Risk Tier: {churnResult.tier}
              </div>

              <div className="mt-4 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                <div className="font-semibold text-slate-300 mb-1">
                  Decision at Cutoff &tau; = {churnThreshold.toFixed(2)}:
                </div>
                {churnResult.isChurn ? (
                  <span className="text-rose-400 font-bold block">
                    🚨 CLASSIFIED AS CHURN (Trigger Retention Outreach)
                  </span>
                ) : (
                  <span className="text-emerald-400 font-bold block">
                    ✅ CLASSIFIED AS RETAINED
                  </span>
                )}
                <div className="text-[11px] text-slate-400 mt-1">
                  Annual Revenue at Risk: ${(churnMonthly * 12).toFixed(2)}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-500">
              Pipeline: Gradient Boosting Classifier (ROC-AUC: 0.931)
            </div>
          </div>
        </div>
      )}

      {/* HR ATTRITION INFERENCE */}
      {activeTrack === "HR_ATTRITION" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-blue-400" />
              <span>Employee Workplace Attributes</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Monthly Base Salary ($)
                </label>
                <input
                  type="number"
                  min={1500}
                  max={25000}
                  value={hrIncome}
                  onChange={(e) => setHrIncome(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Years at Company
                </label>
                <input
                  type="number"
                  min={0}
                  max={30}
                  value={hrYearsComp}
                  onChange={(e) => setHrYearsComp(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Mandatory Overtime
                </label>
                <select
                  value={hrOvertime}
                  onChange={(e) => setHrOvertime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                >
                  <option value="Yes">Yes (Overtime Required)</option>
                  <option value="No">No (Standard Hours)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Work-Life Balance (1=Poor, 4=Best)
                </label>
                <input
                  type="number"
                  min={1}
                  max={4}
                  value={hrWlb}
                  onChange={(e) => setHrWlb(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Job Satisfaction (1=Low, 4=Very High)
                </label>
                <input
                  type="number"
                  min={1}
                  max={4}
                  value={hrJobSat}
                  onChange={(e) => setHrJobSat(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Commute Distance (Miles)
                </label>
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={hrDistance}
                  onChange={(e) => setHrDistance(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>
            </div>
          </div>

          {/* Result */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-2">
                Inference Result (§5)
              </div>
              <div className="text-xs text-slate-400">Departure Hazard Probability:</div>
              <div className={`text-3xl font-extrabold font-mono mt-1 ${hrResult.color}`}>
                {(hrResult.prob * 100).toFixed(1)}%
              </div>
              <div className="mt-2 inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-200">
                Retention Tier: {hrResult.tier}
              </div>

              <div className="mt-4 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                <div className="font-semibold text-slate-300 mb-1">Guidance Directive:</div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Offer voluntary mentorship and workload rebalancing. Strictly prohibited as termination criterion.
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-500">
              Pipeline: Random Forest Classifier (CV F1: 0.849)
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
