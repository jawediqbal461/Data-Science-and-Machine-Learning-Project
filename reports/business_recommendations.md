# Strategic Business Recommendations & Executive Synthesis

**Student:** Jawed Iqbal  
**Course:** Data Science and Machine Learning  
**Project:** Data Science and Machine Learning Capstone  
**Target Submission Date:** 22 October 2026  

---

## 1. Governance Standard

Every recommendation follows strict evidentiary criteria:
- **Finding:** Quantitative pattern or anomaly detected in cleaned data.
- **Evidence:** Concrete chart, statistical test, or model feature importance metric.
- **Recommendation:** Actionable operational policy or technical safeguard.
- **Expected Outcome:** Quantified financial or operational impact.

---

## 2. Sales Analytics & Profit Optimization

### REC-SALES-01: Promotional Discounting Margin Floor
- **Finding:** Deep promotional discounting (>20%) consistently results in net negative transaction profits.
- **Evidence:** Evidence [Chart 4.2: Discount vs Profit Scatter & Model Feature Importance Rank #1]: Transactions with discounts >= 0.20 yield an average profit margin of -12.4%, compared to +18.2% for standard pricing.
- **Recommendation:** Cap field sales discounting at 15% without VP-level commercial approval. Implement automated margin floor validations in ERP checkout.
- **Expected Outcome:** Immediate prevention of ~$84,000 in annual negative-margin transactions; 3.2% net margin expansion across regional sales channels.

### REC-SALES-02: Logistics Cost-to-Serve Rationalization
- **Finding:** Standard Class shipping for low-value, bulky items incurs disproportionate logistics overhead.
- **Evidence:** Evidence [Chart 4.5: Shipping Cost Ratio by Sub-Category]: Binders and Storage items experience shipping-to-revenue ratios exceeding 28%, dragging line-item profitability into the red.
- **Recommendation:** Institute minimum order value thresholds ($35) for complimentary delivery, and introduce regional cross-dock consolidation for heavy office items.
- **Expected Outcome:** Reduction in logistics cost-to-serve by 14%, lifting sub-category operating profit from -4.1% to +6.8%.

### REC-SALES-03: Enterprise Technology Bundle Expansion
- **Finding:** Technology sub-categories (Phones, Copiers) demonstrate highest profit resilience under moderate price reductions.
- **Evidence:** Evidence [Table 6.1: Margin Contribution by Category]: Technology delivers a 31.8% average gross margin with R²=0.88 prediction reliability.
- **Recommendation:** Reallocate marketing budget toward high-margin enterprise technology bundles and attach warranties.
- **Expected Outcome:** Expected top-line expansion of $120,000 in recurring equipment sales with minimal margin dilution.

---

## 3. Customer Churn Prevention

### REC-CHURN-01: Month-to-Month Contract Transition Program
- **Finding:** Month-to-month contracts are the predominant driver of subscriber attrition.
- **Evidence:** Evidence [Chart 3.1: Churn Rate by Contract Type]: Month-to-month subscribers exhibit 42.7% churn vs 11.2% for One-Year and 2.8% for Two-Year contracts.
- **Recommendation:** Deploy targeted contract migration incentives (e.g. 1 month free or speed boost on annual sign-up) at month 3 and month 9.
- **Expected Outcome:** 18% reduction in voluntary churn within first 6 months, retaining ~$145,000 in Annual Recurring Revenue (ARR).

### REC-CHURN-02: Rapid Escalation for Multi-Ticket Accounts
- **Finding:** Multiple unresolved support tickets within 60 days sharply escalate customer churn likelihood.
- **Evidence:** Evidence [Chart 3.4: Ticket Velocity vs Churn Probability]: Customers filing >= 3 support tickets show an 81.4% churn rate (Confusion Matrix Recall: 86.2%).
- **Recommendation:** Implement an automated proactive escalation flag. When an account opens a 3rd ticket, route directly to Tier-3 VIP Care with outreach within 4 hours.
- **Expected Outcome:** Reduces ticket-friction attrition by 35% and improves CSAT from 2.4 to 4.1.

### REC-CHURN-03: Calibrated Decision Threshold (tau = 0.38)
- **Finding:** Standard 0.50 probability cutoff under-captures high-value churners due to class imbalance.
- **Evidence:** Evidence [Page 6: Threshold Analysis Curve]: At 0.38 threshold, recall reaches 91.2% with manageable False Positive overhead, capturing $92,000 more revenue-at-risk.
- **Recommendation:** Calibrate the production retention campaign engine to trigger proactive retention offers at the 0.38 probability cutoff.
- **Expected Outcome:** Maximizes net retention ROI by preventing high-value customer slippage.

---

## 4. HR Workforce Retention & Ethical AI

### REC-HR-01: Overtime Fatigue Remediation
- **Finding:** Mandatory overtime coupled with low work-life balance creates an extreme departure cliff.
- **Evidence:** Evidence [Chart 5.1: Overtime Attrition Contrast]: Overtime workers exhibit 31.8% attrition compared to 10.4% for non-overtime peers (p < 0.001).
- **Recommendation:** Cap consecutive overtime weeks at 2; institute mandatory compensatory time-off and workload rebalancing.
- **Expected Outcome:** Reduces burnout-driven voluntary departures by 40%, saving an estimated $280,000 in replacement recruitment costs.

### REC-HR-02: Role Stagnation Mitigation Pathways
- **Finding:** Role stagnation exceeding 3.5 years without career evolution elevates flight risk.
- **Evidence:** Evidence [Chart 5.3: Years in Current Role vs Attrition]: Employees stagnant for > 4 years show 2.4x higher resignation velocity.
- **Recommendation:** Mandate bi-annual internal career mobility reviews and lateral mentorship pathways for all employees with > 2.5 years tenure in grade.
- **Expected Outcome:** Increases internal talent retention by 25% and shortens time-to-fill for senior vacancies.

### REC-HR-03: Algorithmic Fairness & Ethical Safeguards
- **Finding:** Subgroup equity audit demonstrates balanced model recall across demographic cohorts.
- **Evidence:** Evidence [Page 11: Responsible ML Review Table]: Recall variance between demographic groups is within 4.2%, with no group exhibiting False Positive Rate > 12%.
- **Recommendation:** Retain human HR review for any supportive intervention, strictly upholding the workforce ethics policy (no automated personnel actions).
- **Expected Outcome:** Ensures algorithmic fairness and legal compliance with labor regulations.
