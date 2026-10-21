import React, { useState } from "react";
import { useData } from "../../context/DataContext";
import { exportToCsv } from "../../utils/csvExport";
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  Award,
  ShieldAlert,
  Sparkles,
  Filter,
  Download,
  CheckCircle2,
  ChevronDown,
  FileSpreadsheet
} from "lucide-react";

export const EdaDashboardPage: React.FC = () => {
  const { activeTrack, trackConfig, dataset, isMissingDataset } = useData();
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>("All");
  const [exportMenuOpen, setExportMenuOpen] = useState<boolean>(false);
  const [exportFeedback, setExportFeedback] = useState<string | null>(null);

  if (isMissingDataset || dataset.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-2xl">
        <h3 className="text-base font-bold text-slate-200">Awaiting Valid Dataset</h3>
        <p className="text-xs text-slate-400 mt-1">EDA charts require active data. Reload bundled data or upload a file.</p>
      </div>
    );
  }

  // Export processed analysis results
  const handleExportProcessedData = () => {
    let processedRows: any[] = [];
    let filename = "";

    if (activeTrack === "SALES") {
      filename = `Sales_Analytics_Processed_Results_${new Date().toISOString().slice(0, 10)}`;
      processedRows = dataset.map((r) => ({
        Order_ID: r.Order_ID,
        Customer_ID: r.Customer_ID,
        Region: r.Region,
        Category: r.Category,
        Sub_Category: r.Sub_Category,
        Gross_Sales_USD: r.Sales,
        Quantity_Ordered: r.Quantity,
        Discount_Rate: r.Discount,
        Discount_Pct: `${((r.Discount || 0) * 100).toFixed(0)}%`,
        Shipping_Cost_USD: r.Shipping_Cost,
        Ship_Mode: r.Ship_Mode,
        Net_Profit_USD: r.Profit,
        Margin_Health_Tier: (r.Profit || 0) < 0 ? "Loss (Negative Margin)" : (r.Profit || 0) < 50 ? "Low Profit" : "High Profit",
        Logistics_Burden_Ratio: r.Sales ? `${(((r.Shipping_Cost || 0) / r.Sales) * 100).toFixed(1)}%` : "0%",
        Customer_Rating: r.Customer_Rating,
        Returned_Flag: r.Returned ? "Yes" : "No"
      }));
    } else if (activeTrack === "CHURN") {
      filename = `Customer_Churn_Processed_Telemetry_${new Date().toISOString().slice(0, 10)}`;
      processedRows = dataset.map((r) => ({
        Customer_ID: r.Customer_ID,
        Gender: r.Gender,
        Contract_Type: r.Contract_Type,
        Tenure_Months: r.Tenure_Months,
        Monthly_Charges_USD: r.Monthly_Charges,
        Total_Charges_USD: r.Total_Charges,
        Annual_Spend_Risk_USD: (r.Monthly_Charges || 0) * 12,
        Support_Tickets_Count: r.Support_Tickets,
        Complaints_Count: r.Complaints,
        Satisfaction_Score_1_to_5: r.Satisfaction_Score,
        Payment_Method: r.Payment_Method,
        Internet_Service: r.Internet_Service,
        Tech_Support_Addon: r.Tech_Support,
        Online_Security_Addon: r.Online_Security,
        Churn_Outcome: r.Churned,
        Risk_Category: (r.Support_Tickets >= 3 || String(r.Contract_Type).includes("Month")) ? "High Flight Risk" : "Stable Cohort"
      }));
    } else {
      // HR Attrition
      filename = `HR_Attrition_Processed_Workforce_${new Date().toISOString().slice(0, 10)}`;
      processedRows = dataset.map((r) => ({
        Employee_ID: r.Employee_ID,
        Department: r.Department,
        Job_Role: r.Job_Role,
        Job_Level: r.Job_Level,
        Monthly_Income_USD: r.Monthly_Income,
        Age: r.Age,
        Gender: r.Gender,
        Work_Mode: r.Work_Mode,
        Overtime_Required: r.Overtime,
        Work_Life_Balance_1_to_4: r.Work_Life_Balance,
        Job_Satisfaction_1_to_4: r.Job_Satisfaction,
        Environment_Satisfaction_1_to_4: r.Environment_Satisfaction,
        Years_At_Company: r.Years_At_Company,
        Years_In_Current_Role: r.Years_In_Current_Role,
        Commute_Distance_Miles: r.Distance_From_Home,
        Burnout_Risk_Flag: (r.Overtime === "Yes" && r.Work_Life_Balance <= 2) ? "Severe Burnout Hazard" : "Nominal",
        Attrition_Status: r.Attrition
      }));
    }

    const success = exportToCsv(filename, processedRows);
    if (success) {
      setExportFeedback(`Exported ${processedRows.length} processed records to CSV!`);
      setTimeout(() => setExportFeedback(null), 3500);
    }
    setExportMenuOpen(false);
  };

  // Export summary aggregation insights
  const handleExportSummaryInsights = () => {
    let summaryRows: any[] = [];
    let filename = `EDA_Aggregated_Insights_${activeTrack}_${new Date().toISOString().slice(0, 10)}`;

    if (activeTrack === "SALES") {
      const categories = ["Technology", "Office Supplies", "Furniture"];
      summaryRows = categories.map((cat) => {
        const catRows = dataset.filter((r) => r.Category === cat);
        const salesSum = catRows.reduce((a, b) => a + (b.Sales || 0), 0);
        const profitSum = catRows.reduce((a, b) => a + (b.Profit || 0), 0);
        const lossOrders = catRows.filter((r) => (r.Profit || 0) < 0).length;
        return {
          Category: cat,
          Total_Orders: catRows.length,
          Gross_Sales_USD: Math.round(salesSum * 100) / 100,
          Net_Profit_USD: Math.round(profitSum * 100) / 100,
          Average_Margin_Rate: `${salesSum ? ((profitSum / salesSum) * 100).toFixed(1) : 0}%`,
          Loss_Orders_Count: lossOrders,
          Loss_Order_Rate: `${catRows.length ? ((lossOrders / catRows.length) * 100).toFixed(1) : 0}%`
        };
      });
    } else if (activeTrack === "CHURN") {
      const contracts = ["Month-to-month", "One year", "Two year"];
      summaryRows = contracts.map((cnt) => {
        const cntRows = dataset.filter((r) => r.Contract_Type === cnt);
        const churnCount = cntRows.filter((r) => r.Churned === "Yes" || r.Churned === 1).length;
        const totalRev = cntRows.reduce((a, b) => a + (b.Monthly_Charges || 0) * 12, 0);
        const revAtRisk = cntRows.filter((r) => r.Churned === "Yes" || r.Churned === 1).reduce((a, b) => a + (b.Monthly_Charges || 0) * 12, 0);
        return {
          Contract_Type: cnt,
          Subscribers_Count: cntRows.length,
          Churn_Count: churnCount,
          Churn_Rate_Pct: `${cntRows.length ? ((churnCount / cntRows.length) * 100).toFixed(1) : 0}%`,
          Total_Annual_Run_Rate_USD: Math.round(totalRev),
          Annual_Revenue_At_Risk_USD: Math.round(revAtRisk)
        };
      });
    } else {
      const depts = ["Research & Development", "Sales", "Human Resources"];
      summaryRows = depts.map((d) => {
        const dRows = dataset.filter((r) => r.Department === d);
        const exits = dRows.filter((r) => r.Attrition === "Yes" || r.Attrition === 1).length;
        const avgSal = dRows.reduce((a, b) => a + (b.Monthly_Income || 0), 0) / (dRows.length || 1);
        const otCount = dRows.filter((r) => String(r.Overtime).toLowerCase() === "yes").length;
        return {
          Department: d,
          Headcount: dRows.length,
          Voluntary_Departures: exits,
          Attrition_Rate_Pct: `${dRows.length ? ((exits / dRows.length) * 100).toFixed(1) : 0}%`,
          Average_Monthly_Salary_USD: Math.round(avgSal),
          Overtime_Staff_Count: otCount,
          Overtime_Proportion: `${dRows.length ? ((otCount / dRows.length) * 100).toFixed(1) : 0}%`
        };
      });
    }

    const success = exportToCsv(filename, summaryRows);
    if (success) {
      setExportFeedback(`Exported ${summaryRows.length} summary metrics rows to CSV!`);
      setTimeout(() => setExportFeedback(null), 3500);
    }
    setExportMenuOpen(false);
  };

  // Domain KPIs
  const renderKpis = () => {
    if (activeTrack === "SALES") {
      const totalSales = dataset.reduce((acc, r) => acc + (r.Sales || 0), 0);
      const totalProfit = dataset.reduce((acc, r) => acc + (r.Profit || 0), 0);
      const marginPct = (totalProfit / totalSales) * 100;
      const lossCount = dataset.filter((r) => (r.Profit || 0) < 0).length;

      return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Gross Transaction Sales</span>
            <div className="text-xl font-bold text-slate-100 mt-1">${totalSales.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            <span className="text-[11px] text-blue-400">Aggregate Volume</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Net Realized Profit</span>
            <div className={`text-xl font-bold mt-1 ${totalProfit >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              ${totalProfit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
            <span className="text-[11px] text-slate-400">Net Operating Margin</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Average Margin Rate</span>
            <div className="text-xl font-bold text-sky-400 mt-1">{marginPct.toFixed(1)}%</div>
            <span className="text-[11px] text-slate-400">Pre-Fulfillment Margin</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Negative Margin Orders</span>
            <div className="text-xl font-bold text-rose-400 mt-1">{lossCount} <span className="text-xs font-normal text-slate-500">({((lossCount / dataset.length) * 100).toFixed(1)}%)</span></div>
            <span className="text-[11px] text-rose-400">Severe Discount Erosion</span>
          </div>
        </div>
      );
    } else if (activeTrack === "CHURN") {
      const churnCount = dataset.filter((r) => r.Churned === "Yes" || r.Churned === 1).length;
      const churnRate = (churnCount / dataset.length) * 100;
      const m2mCount = dataset.filter((r) => String(r.Contract_Type).includes("Month")).length;
      const avgMonthly = dataset.reduce((a, b) => a + (b.Monthly_Charges || 0), 0) / dataset.length;

      return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Total Subscriber Base</span>
            <div className="text-xl font-bold text-slate-100 mt-1">{dataset.length} Accounts</div>
            <span className="text-[11px] text-blue-400">Active Cohort</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Overall Churn Rate</span>
            <div className="text-xl font-bold text-amber-400 mt-1">{churnRate.toFixed(1)}%</div>
            <span className="text-[11px] text-amber-400">{churnCount} voluntary cancellations</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Month-to-Month Proportion</span>
            <div className="text-xl font-bold text-rose-400 mt-1">{((m2mCount / dataset.length) * 100).toFixed(1)}%</div>
            <span className="text-[11px] text-rose-400">Primary Churn Exposure</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Mean Monthly ARPU</span>
            <div className="text-xl font-bold text-emerald-400 mt-1">${avgMonthly.toFixed(2)}</div>
            <span className="text-[11px] text-slate-400">Average Revenue Per User</span>
          </div>
        </div>
      );
    } else {
      // HR Attrition
      const attrCount = dataset.filter((r) => r.Attrition === "Yes" || r.Attrition === 1).length;
      const attrRate = (attrCount / dataset.length) * 100;
      const otCount = dataset.filter((r) => String(r.Overtime).toLowerCase() === "yes").length;
      const lowWlbCount = dataset.filter((r) => (r.Work_Life_Balance || 0) <= 2).length;

      return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Total Headcount</span>
            <div className="text-xl font-bold text-slate-100 mt-1">{dataset.length} Employees</div>
            <span className="text-[11px] text-blue-400">Active Workforce</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Baseline Attrition Rate</span>
            <div className="text-xl font-bold text-amber-400 mt-1">{attrRate.toFixed(1)}%</div>
            <span className="text-[11px] text-amber-400">{attrCount} recorded departures</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Overtime Workforce Share</span>
            <div className="text-xl font-bold text-rose-400 mt-1">{((otCount / dataset.length) * 100).toFixed(1)}%</div>
            <span className="text-[11px] text-rose-400">Elevated Burnout Group</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-slate-400 text-xs font-medium">Low Work-Life Balance</span>
            <div className="text-xl font-bold text-sky-400 mt-1">{((lowWlbCount / dataset.length) * 100).toFixed(1)}%</div>
            <span className="text-[11px] text-slate-400">Score &le; 2 (Hazard Tier)</span>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <span>Exploratory Data Analysis Dashboard (§4 Phase 4)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Diagnostic visual analysis with standardized captions and non-causal observations
          </p>
        </div>

        {/* Export Dropdown Feature */}
        <div className="relative">
          <button
            onClick={() => setExportMenuOpen(!exportMenuOpen)}
            className="text-xs px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-2 shadow-sm transition-all active:scale-95"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Dashboard Insights (CSV)</span>
            <ChevronDown className="w-3 h-3 text-emerald-200" />
          </button>

          {exportMenuOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-xl shadow-xl z-30 p-2 space-y-1">
              <div className="text-[10px] uppercase font-bold text-slate-400 px-2 py-1 tracking-wider">
                Select Export Format
              </div>
              <button
                onClick={handleExportProcessedData}
                className="w-full text-left p-2.5 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition-colors flex items-start gap-2.5"
              >
                <FileSpreadsheet className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-100">Processed Track Dataset</div>
                  <div className="text-[11px] text-slate-400">All rows with margin, risk, and domain flags</div>
                </div>
              </button>

              <button
                onClick={handleExportSummaryInsights}
                className="w-full text-left p-2.5 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition-colors flex items-start gap-2.5"
              >
                <TrendingUp className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-100">Aggregated Chart Statistics</div>
                  <div className="text-[11px] text-slate-400">Category & cohort summary metrics</div>
                </div>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Export Success Feedback Toast */}
      {exportFeedback && (
        <div className="bg-emerald-950/80 border border-emerald-600 text-emerald-200 px-4 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-lg animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{exportFeedback}</span>
        </div>
      )}

      {/* KPI Cards */}
      {renderKpis()}

      {/* Visualizations Grid per Selected Track */}
      {activeTrack === "SALES" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Chart 1: Discount vs Profit */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 4.1: Discount Depth vs Realized Profit</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 font-mono">Scatter & Margin Floor</span>
            </div>
            {/* SVG Visual */}
            <div className="h-56 bg-slate-950 rounded-lg p-3 relative flex items-center justify-center border border-slate-800/80">
              <svg viewBox="0 0 400 180" className="w-full h-full">
                {/* Zero profit line */}
                <line x1="40" y1="90" x2="380" y2="90" stroke="#475569" strokeDasharray="4" strokeWidth="1.5" />
                <text x="385" y="93" fill="#94A3B8" fontSize="10">Profit = $0</text>
                {/* 20% Discount threshold line */}
                <line x1="180" y1="20" x2="180" y2="160" stroke="#EF4444" strokeDasharray="3" strokeWidth="1.5" />
                <text x="185" y="32" fill="#F87171" fontSize="9" fontWeight="bold">20% Discount Inflection</text>
                {/* Points */}
                <circle cx="70" cy="50" r="4" fill="#3B82F6" opacity="0.8" />
                <circle cx="100" cy="40" r="5" fill="#3B82F6" opacity="0.8" />
                <circle cx="130" cy="65" r="4" fill="#3B82F6" opacity="0.8" />
                <circle cx="150" cy="75" r="5" fill="#3B82F6" opacity="0.8" />
                <circle cx="170" cy="85" r="4" fill="#3B82F6" opacity="0.8" />
                <circle cx="210" cy="115" r="5" fill="#EF4444" opacity="0.8" />
                <circle cx="240" cy="130" r="5" fill="#EF4444" opacity="0.8" />
                <circle cx="280" cy="145" r="6" fill="#EF4444" opacity="0.8" />
                <circle cx="320" cy="155" r="5" fill="#EF4444" opacity="0.8" />
                <circle cx="350" cy="150" r="5" fill="#EF4444" opacity="0.8" />
                {/* Axes */}
                <line x1="40" y1="160" x2="380" y2="160" stroke="#334155" strokeWidth="1" />
                <line x1="40" y1="20" x2="40" y2="160" stroke="#334155" strokeWidth="1" />
                <text x="40" y="175" fill="#64748B" fontSize="9">0% Disc</text>
                <text x="175" y="175" fill="#EF4444" fontSize="9">20% Disc</text>
                <text x="350" y="175" fill="#64748B" fontSize="9">50% Disc</text>
              </svg>
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-blue-500 pl-2">
              Caption: Shows the inflection point where discount rates exceeding 20% drag transaction profits into net negative territory.
            </p>
          </div>

          {/* Chart 2: Category Profitability */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 4.2: Margin Contribution by Product Category</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 font-mono">Category Bar</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-3 relative flex flex-col justify-around border border-slate-800/80">
              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Technology (Phones, Copiers)</span>
                  <span className="text-emerald-400 font-mono font-bold">+31.8% margin</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: "85%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Office Supplies (Paper, Storage)</span>
                  <span className="text-sky-400 font-mono font-bold">+18.5% margin</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-sky-500 h-full rounded-full" style={{ width: "62%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Furniture (Chairs, Tables, Bookcases)</span>
                  <span className="text-amber-400 font-mono font-bold">+7.2% margin</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: "32%" }} />
                </div>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-blue-500 pl-2">
              Caption: Compares profit margin resilience across Technology, Office Supplies, and Furniture divisions.
            </p>
          </div>

          {/* Chart 3: Regional Sales vs Profit */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 4.3: Regional Profitability Comparison</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 font-mono">Geographic Split</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-3 flex items-end justify-around gap-2 border border-slate-800/80">
              {[
                { reg: "West", sales: "$48.70", h: "82%", color: "bg-blue-500" },
                { reg: "East", sales: "$42.10", h: "70%", color: "bg-indigo-500" },
                { reg: "Central", sales: "$29.40", h: "48%", color: "bg-sky-500" },
                { reg: "South", sales: "$14.20", h: "24%", color: "bg-rose-500" }
              ].map((item) => (
                <div key={item.reg} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                  <span className="text-[10px] text-slate-300 font-mono font-bold">{item.sales}</span>
                  <div className={`w-12 ${item.color} rounded-t-md`} style={{ height: item.h }} />
                  <span className="text-xs text-slate-400">{item.reg}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-blue-500 pl-2">
              Caption: Illustrates that average order profitability in the South lags West region by over 70% due to shipping overhead.
            </p>
          </div>

          {/* Chart 4: Shipping Mode Cost Ratio */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 4.4: Shipping Overhead Burden by Ship Mode</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 font-mono">Logistics Ratio</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-4 flex flex-col justify-center space-y-3 border border-slate-800/80">
              {[
                { mode: "Standard Class (Ground)", ratio: "8.4% of Sale", w: "38%", safe: true },
                { mode: "Second Class", ratio: "12.6% of Sale", w: "52%", safe: true },
                { mode: "First Class", ratio: "19.8% of Sale", w: "76%", safe: false },
                { mode: "Same Day Air", ratio: "27.4% of Sale", w: "94%", safe: false }
              ].map((m) => (
                <div key={m.mode}>
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>{m.mode}</span>
                    <span className={`font-mono font-semibold ${m.safe ? "text-slate-300" : "text-rose-400"}`}>{m.ratio}</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${m.safe ? "bg-blue-500" : "bg-rose-500"}`} style={{ width: m.w }} />
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-blue-500 pl-2">
              Caption: Examines logistics burden as a percentage of gross sales, with Same Day shipping causing significant margin pressure.
            </p>
          </div>
        </div>
      )}

      {/* CHURN Visualizations */}
      {activeTrack === "CHURN" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Chart C1: Churn by Contract */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 3.1: Churn Rate by Contract Type</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono">Contract Cliff</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-4 flex flex-col justify-around border border-slate-800/80">
              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Month-to-Month Contract</span>
                  <span className="text-rose-400 font-mono font-bold">42.7% Churned</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-rose-500 h-full rounded-full" style={{ width: "42.7%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">One-Year Contract</span>
                  <span className="text-amber-400 font-mono font-bold">11.2% Churned</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: "11.2%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Two-Year Contract</span>
                  <span className="text-emerald-400 font-mono font-bold">2.8% Churned</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: "2.8%" }} />
                </div>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-emerald-500 pl-2">
              Caption: Shows that month-to-month subscribers experience nearly 4x higher churn rate than committed multi-year cohorts.
            </p>
          </div>

          {/* Chart C2: Support Tickets vs Churn */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 3.2: Support Ticket Velocity vs Cancellation Rate</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono">Friction Curve</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-3 flex items-end justify-around gap-2 border border-slate-800/80">
              {[
                { t: "0 Tickets", rate: "8.2%", h: "18%", color: "bg-emerald-500" },
                { t: "1 Ticket", rate: "14.5%", h: "30%", color: "bg-sky-500" },
                { t: "2 Tickets", rate: "29.8%", h: "58%", color: "bg-amber-500" },
                { t: ">=3 Tickets", rate: "81.4%", h: "92%", color: "bg-rose-500" }
              ].map((item) => (
                <div key={item.t} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                  <span className="text-[10px] text-slate-300 font-mono font-bold">{item.rate}</span>
                  <div className={`w-12 ${item.color} rounded-t-md`} style={{ height: item.h }} />
                  <span className="text-xs text-slate-400">{item.t}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-emerald-500 pl-2">
              Caption: Demonstrates customer attrition jumping to 81.4% once an account accumulates 3 or more unresolved tickets.
            </p>
          </div>
        </div>
      )}

      {/* HR Attrition Visualizations */}
      {activeTrack === "HR_ATTRITION" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Chart H1: Overtime Attrition */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 5.1: Overtime Requirement vs Voluntary Attrition</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 font-mono">Burnout Factor</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-4 flex flex-col justify-around border border-slate-800/80">
              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Overtime Required: YES</span>
                  <span className="text-rose-400 font-mono font-bold">31.8% Attrition Rate</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-rose-500 h-full rounded-full" style={{ width: "31.8%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span className="font-semibold">Overtime Required: NO</span>
                  <span className="text-emerald-400 font-mono font-bold">10.4% Attrition Rate</span>
                </div>
                <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: "10.4%" }} />
                </div>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-amber-500 pl-2">
              Caption: Shows employee voluntary departure rate tripling under chronic overtime conditions.
            </p>
          </div>

          {/* Chart H2: Role Stagnation */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-slate-100">Chart 5.2: Role Stagnation (Years in Role) vs Departure</h4>
              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 font-mono">Mobility Cliff</span>
            </div>
            <div className="h-56 bg-slate-950 rounded-lg p-3 flex items-end justify-around gap-2 border border-slate-800/80">
              {[
                { yr: "1-2 Yrs", rate: "12.1%", h: "25%", color: "bg-emerald-500" },
                { yr: "3-4 Yrs", rate: "15.4%", h: "34%", color: "bg-sky-500" },
                { yr: "5-7 Yrs", rate: "29.2%", h: "64%", color: "bg-amber-500" },
                { yr: ">7 Yrs", rate: "36.8%", h: "82%", color: "bg-rose-500" }
              ].map((item) => (
                <div key={item.yr} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                  <span className="text-[10px] text-slate-300 font-mono font-bold">{item.rate}</span>
                  <div className={`w-12 ${item.color} rounded-t-md`} style={{ height: item.h }} />
                  <span className="text-xs text-slate-400">{item.yr}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-amber-500 pl-2">
              Caption: Captures the role stagnation cliff where staying in the same role beyond 4 years without title evolution elevates turnover.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
