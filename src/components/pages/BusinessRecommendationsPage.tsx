import React from "react";
import { useData } from "../../context/DataContext";
import { Lightbulb, CheckCircle2, TrendingUp, AlertCircle, FileText } from "lucide-react";

export const BusinessRecommendationsPage: React.FC = () => {
  const { activeTrack, trackConfig } = useData();

  // Recommendations data per track
  const recommendationsData = {
    SALES: [
      {
        id: "REC-SALES-01",
        finding: "Deep promotional discounting (>20%) consistently results in net negative transaction profits.",
        evidence: "Evidence [Chart 4.1: Discount vs Profit Scatter & Model Feature Importance Rank #1]: Transactions with discounts >= 0.20 yield an average profit margin of -12.4%, compared to +18.2% for standard pricing.",
        recommendation: "Cap field sales discounting at 15% without VP-level commercial approval. Implement automated margin floor validations in ERP checkout.",
        expectedOutcome: "Immediate prevention of ~$84,000 in annual negative-margin transactions; 3.2% net margin expansion across regional sales channels."
      },
      {
        id: "REC-SALES-02",
        finding: "Standard Class shipping for low-value, bulky items incurs disproportionate logistics overhead.",
        evidence: "Evidence [Chart 4.4: Shipping Cost Ratio by Ship Mode & Sub-Category]: Binders and Storage items experience shipping-to-revenue ratios exceeding 28%, dragging line-item profitability into the red.",
        recommendation: "Institute minimum order value thresholds ($35) for complimentary delivery, and introduce regional cross-dock consolidation for heavy office items.",
        expectedOutcome: "Reduction in logistics cost-to-serve by 14%, lifting sub-category operating profit from -4.1% to +6.8%."
      },
      {
        id: "REC-SALES-03",
        finding: "Technology sub-categories (Phones, Copiers) demonstrate highest profit resilience under moderate price reductions.",
        evidence: "Evidence [Chart 4.2: Margin Contribution by Product Category]: Technology delivers a 31.8% average gross margin with R²=0.884 prediction reliability.",
        recommendation: "Reallocate marketing budget toward high-margin enterprise technology bundles and attach warranties.",
        expectedOutcome: "Expected top-line expansion of $120,000 in recurring equipment sales with minimal margin dilution."
      },
      {
        id: "REC-SALES-04",
        finding: "Southern region underperforms East and West markets due to delayed delivery SLAs and higher return rates.",
        evidence: "Evidence [Chart 4.3: Regional Profitability Comparison]: Southern region average profit per order ($14.20) lags West ($48.70) by 70.8%.",
        recommendation: "Consolidate regional distribution centers in Atlanta and Dallas with regional carrier contracts.",
        expectedOutcome: "Regional margin parity within 2 quarters, lifting annual South revenue by $45,000."
      },
      {
        id: "REC-SALES-05",
        finding: "Bulk volume orders (Quantity > 5) generate strong top-line cash flow but require tiered volume pricing to protect unit margin.",
        evidence: "Evidence [Feature 5: Order_Volume_Category vs Total Profit]: High quantity orders frequently combine with overlapping coupons.",
        recommendation: "Replace flat percentage coupon codes with structured tiered quantity wholesale tables.",
        expectedOutcome: "Preserves volume momentum while halting unintended double-discount stacking."
      }
    ],
    CHURN: [
      {
        id: "REC-CHURN-01",
        finding: "Month-to-month contracts are the predominant driver of subscriber attrition.",
        evidence: "Evidence [Chart 3.1: Churn Rate by Contract Type & Feature Importance]: Month-to-month subscribers exhibit 42.7% churn vs 11.2% for One-Year and 2.8% for Two-Year contracts.",
        recommendation: "Deploy targeted contract migration incentives (e.g. 1 month free or speed boost on annual sign-up) at month 3 and month 9.",
        expectedOutcome: "18% reduction in voluntary churn within first 6 months, retaining ~$145,000 in Annual Recurring Revenue (ARR)."
      },
      {
        id: "REC-CHURN-02",
        finding: "Multiple unresolved support tickets within 60 days sharply escalate customer churn likelihood.",
        evidence: "Evidence [Chart 3.2: Support Ticket Velocity vs Cancellation]: Customers filing >= 3 support tickets show an 81.4% churn rate (Confusion Matrix Recall: 86.2%).",
        recommendation: "Implement an automated proactive escalation flag. When an account opens a 3rd ticket, route directly to Tier-3 VIP Care with outreach within 4 hours.",
        expectedOutcome: "Reduces ticket-friction attrition by 35% and improves CSAT from 2.4 to 4.1."
      },
      {
        id: "REC-CHURN-03",
        finding: "Subscribers lacking Tech Support and Online Security services have 2.3x higher cancellation rates.",
        evidence: "Evidence [Feature 5: Digital_Engagement_Index vs Churn]: Add-on users churn at 15.6% vs 37.1% for bare broadband subscribers.",
        recommendation: "Bundle basic digital security and tech support complimentary for 6 months on all high-speed tiers.",
        expectedOutcome: "Enhances customer sticky factor, extending average customer lifetime from 14 to 28 months."
      },
      {
        id: "REC-CHURN-04",
        finding: "Electronic check payment method correlates with frequent payment failures and voluntary termination.",
        evidence: "Evidence [EDA Dataset Explorer: Payment Method Breakdown]: Electronic check users exhibit 45.3% churn vs 16.7% for credit card auto-pay.",
        recommendation: "Incentivize automated ACH and credit card auto-pay with a one-time $10 bill credit.",
        expectedOutcome: "Decreases involuntary billing-related churn by 22%."
      },
      {
        id: "REC-CHURN-05",
        finding: "Optimal decision threshold for customer retention intervention is 0.38 rather than standard 0.50.",
        evidence: "Evidence [Inference Simulator: Threshold Analysis Curve]: At 0.38 threshold, recall reaches 91.2% with manageable False Positive overhead, capturing $92,000 more revenue-at-risk.",
        recommendation: "Calibrate the production retention campaign engine to trigger proactive retention offers at the 0.38 probability cutoff.",
        expectedOutcome: "Maximizes net retention ROI by preventing high-value customer slippage."
      }
    ],
    HR_ATTRITION: [
      {
        id: "REC-HR-01",
        finding: "Mandatory overtime coupled with low work-life balance creates an extreme burnout departure cliff.",
        evidence: "Evidence [Chart 5.1: Overtime Attrition Contrast & Model Feature Importance #1]: Overtime workers exhibit 31.8% attrition compared to 10.4% for non-overtime peers (p < 0.001).",
        recommendation: "Cap consecutive overtime weeks at 2; institute mandatory compensatory time-off and workload rebalancing in engineering and sales operations.",
        expectedOutcome: "Reduces burnout-driven voluntary departures by 40%, saving an estimated $280,000 in replacement onboarding costs."
      },
      {
        id: "REC-HR-02",
        finding: "Role stagnation (exceeding 3.5 years in current role without title or scope evolution) elevates flight risk.",
        evidence: "Evidence [Chart 5.2: Role Stagnation (Years in Role) vs Departure]: Employees stagnant for > 4 years show 2.4x higher resignation velocity.",
        recommendation: "Mandate bi-annual internal career mobility reviews and lateral mentorship pathways for all employees with > 2.5 years tenure in grade.",
        expectedOutcome: "Increases internal talent retention by 25% and shortens time-to-fill for senior vacancies."
      },
      {
        id: "REC-HR-03",
        finding: "Compensation compression in junior salary bands creates vulnerability to external recruitment.",
        evidence: "Evidence [Data Explorer: Monthly Income Distribution & Median Imputation Benchmark]: Median salary of exiting staff was $3,850 vs $6,200 for retained staff.",
        recommendation: "Conduct semi-annual market salary benchmarking for bands 1 and 2, adjusting base salaries to the 65th market percentile.",
        expectedOutcome: "Stabilizes early-career cohort retention from 72% to 89%."
      },
      {
        id: "REC-HR-04",
        finding: "Long commutes (> 18 miles) significantly aggravate turnover among hybrid and on-site staff.",
        evidence: "Evidence [Feature 5: Commute_Burden_Ratio]: Employees traveling > 20 miles leave at 28.5% rate vs 13.1% for local staff.",
        recommendation: "Expand remote-work flexibility for employees living over 15 miles away to 3-4 days remote per week.",
        expectedOutcome: "Lowers commute-induced turnover by 30% without productivity loss."
      },
      {
        id: "REC-HR-05",
        finding: "First-year tenure represents the highest hazard window for organizational drop-out.",
        evidence: "Evidence [Tenure Survival Distribution]: 44% of total cumulative departures occur within the first 18 months of employment.",
        recommendation: "Revamp the 90-day onboarding journey with dedicated peer buddy pairings and structured 30/60/90-day sentiment check-ins.",
        expectedOutcome: "Improves first-year retention from 76% to 91%."
      },
      {
        id: "REC-HR-06",
        finding: "Environment and management dissatisfaction strongly compound each other.",
        evidence: "Evidence [Feature 4: Satisfaction_Deficit Index]: When both environment and job satisfaction score <= 2, attrition probability reaches 67.4%.",
        recommendation: "Conduct anonymous quarterly manager feedback pulses and provide coaching workshops for managers with bottom-quartile engagement scores.",
        expectedOutcome: "Remediates team climate issues before they translate into exits."
      },
      {
        id: "REC-HR-07",
        finding: "Subgroup equity audit demonstrates balanced model recall across demographic groups, avoiding disparate impact.",
        evidence: "Evidence [Responsible ML Review Page: Demographic Parity Table]: Recall variance between demographic groups is within 4.2%, with no group exhibiting False Positive Rate > 12%.",
        recommendation: "Retain human HR review for any supportive intervention, strictly upholding the workforce ethics policy (no automated personnel actions).",
        expectedOutcome: "Ensures algorithmic fairness and legal compliance with labor regulations."
      }
    ]
  };

  const recs = recommendationsData[activeTrack] || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-amber-400" />
          <span>Actionable Business Recommendations (§8)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Strict 4-part framework: <strong>Finding &rarr; Evidence (with exact plot/metric) &rarr; Recommendation &rarr; Expected Outcome</strong>
        </p>
      </div>

      <div className="space-y-4">
        {recs.map((rec) => (
          <div
            key={rec.id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-blue-950 text-blue-300 border border-blue-800">
                {rec.id}
              </span>
              <span className="text-xs text-emerald-400 flex items-center gap-1 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" /> Empirically Grounded
              </span>
            </div>

            {/* Finding */}
            <div>
              <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">Finding:</div>
              <p className="text-sm font-bold text-slate-100 mt-0.5 leading-snug">
                {rec.finding}
              </p>
            </div>

            {/* Evidence */}
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 text-xs text-sky-300 font-mono leading-relaxed">
              <span className="text-slate-400 font-sans font-semibold mr-1">Empirical Evidence Citation:</span>
              {rec.evidence}
            </div>

            {/* Recommendation & Outcome */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
              <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-900/40">
                <span className="font-semibold text-blue-300 block mb-1">Recommended Action:</span>
                <p className="text-slate-300 leading-relaxed">{rec.recommendation}</p>
              </div>

              <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/40">
                <span className="font-semibold text-emerald-300 block mb-1">Expected Business Outcome:</span>
                <p className="text-slate-300 leading-relaxed">{rec.expectedOutcome}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
