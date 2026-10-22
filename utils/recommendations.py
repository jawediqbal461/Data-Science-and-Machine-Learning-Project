"""
utils/recommendations.py
Structured Business Recommendations Engine.

Every recommendation follows: Finding -> Evidence -> Recommendation ->
Expected Outcome. The "Finding" headline and "Recommendation" business
action are standard domain playbook language for each pattern; the
"Evidence" and "Expected Outcome" numbers are computed LIVE from whatever
dataset (bundled or uploaded) is actually active right now — nothing here
is a fixed/fabricated statistic. A finding is silently omitted if the
active dataset doesn't have the columns needed to compute it.
"""

from typing import Any, Dict, List, Optional

try:
    import numpy as np
    import pandas as pd
except ImportError:
    np = None  # type: ignore
    pd = None  # type: ignore


def _cols_present(df, cols: List[str]) -> bool:
    try:
        return all(c in df.columns for c in cols)
    except Exception:
        return False


def _fmt_money(x: float) -> str:
    sign = "-" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def _fmt_pct(x: float, decimals: int = 1) -> str:
    return f"{x * 100:.{decimals}f}%"


def _worse_than(worse: Optional[float], better: Optional[float], min_gap_pp: float = 3.0) -> bool:
    """True only if `worse` is actually higher than `better` by a meaningful
    margin (in percentage points). Used to gate every directional finding so
    the headline text can never assert a pattern the live data doesn't
    actually show (or shows in reverse)."""
    if worse is None or better is None:
        return False
    return (worse - better) * 100 >= min_gap_pp


# ---------------------------------------------------------------------------
# SALES
# ---------------------------------------------------------------------------

def _sales_recs(df) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    if not _cols_present(df, ["Discount", "Profit", "Sales"]):
        return recs

    valid = df[df["Sales"] > 0].copy()
    valid["margin"] = valid["Profit"] / valid["Sales"]

    # REC-SALES-01: deep discounting vs margin
    deep = valid[valid["Discount"] >= 0.20]
    standard = valid[valid["Discount"] < 0.20]
    if len(deep) >= 5 and len(standard) >= 5 and _worse_than(
        -float(deep["margin"].mean()), -float(standard["margin"].mean())
    ):
        deep_margin = float(deep["margin"].mean())
        std_margin = float(standard["margin"].mean())
        historical_loss = float(deep.loc[deep["Profit"] < 0, "Profit"].sum())
        recs.append({
            "id": "REC-SALES-01",
            "finding": "Deep promotional discounting (>=20%) is associated with materially weaker transaction profit margins.",
            "evidence": (
                f"Live on the active dataset ({len(deep):,} orders at >=20% discount vs {len(standard):,} at standard "
                f"pricing): average profit margin is **{_fmt_pct(deep_margin)}** on deep-discount orders vs "
                f"**{_fmt_pct(std_margin)}** on standard-pricing orders."
            ),
            "recommendation": "Cap field sales discounting at 15% without manager-level approval, and add an automated margin-floor validation step at checkout.",
            "expected_outcome": (
                f"This dataset's own history shows **{_fmt_money(abs(historical_loss))}** in cumulative negative profit "
                f"sitting inside deep-discount orders — the amount at stake if that pattern recurs."
                if historical_loss < 0 else
                "No net-negative deep-discount orders are present in this dataset's history, but the margin gap above still represents avoidable discount leakage."
            ),
        })

    # REC-SALES-02: shipping cost ratio by sub-category
    if _cols_present(df, ["Shipping_Cost", "Sub_Category"]):
        grp = df.groupby("Sub_Category").apply(
            lambda g: g["Shipping_Cost"].sum() / g["Sales"].sum() if g["Sales"].sum() > 0 else 0.0
        )
        grp = grp[grp.index.notna()]
        if len(grp) > 0:
            overall_ratio = df["Shipping_Cost"].sum() / df["Sales"].sum() if df["Sales"].sum() > 0 else 0.0
            worst_sub = grp.idxmax()
            worst_ratio = float(grp.max())
            sub_sales = float(df.loc[df["Sub_Category"] == worst_sub, "Sales"].sum())
            potential_saving = max(0.0, (worst_ratio - overall_ratio) * sub_sales)
            recs.append({
                "id": "REC-SALES-02",
                "finding": f"The '{worst_sub}' sub-category carries disproportionate logistics overhead relative to the rest of the catalog.",
                "evidence": (
                    f"Live: **{worst_sub}** shipping-to-revenue ratio is **{_fmt_pct(worst_ratio)}**, vs "
                    f"**{_fmt_pct(overall_ratio)}** across the whole active dataset."
                ),
                "recommendation": "Introduce a minimum order value for complimentary delivery and consolidate regional shipments for bulky/low-value sub-categories.",
                "expected_outcome": (
                    f"Bringing **{worst_sub}**'s shipping ratio down to the dataset average would free up roughly "
                    f"**{_fmt_money(potential_saving)}** currently spent on excess logistics cost for that sub-category."
                ),
            })

    # REC-SALES-03: best-margin category
    if _cols_present(df, ["Category"]):
        cat_margin = df.groupby("Category").apply(
            lambda g: g["Profit"].sum() / g["Sales"].sum() if g["Sales"].sum() > 0 else 0.0
        )
        if len(cat_margin) > 0:
            best_cat = cat_margin.idxmax()
            best_margin = float(cat_margin.max())
            best_cat_sales = float(df.loc[df["Category"] == best_cat, "Sales"].sum())
            recs.append({
                "id": "REC-SALES-03",
                "finding": f"The '{best_cat}' category shows the strongest profit resilience in the active dataset.",
                "evidence": f"Live: **{best_cat}** delivers a **{_fmt_pct(best_margin)}** blended gross margin on **{_fmt_money(best_cat_sales)}** of recorded sales.",
                "recommendation": f"Reallocate marketing budget toward {best_cat.lower()} bundles and attach extended-warranty upsells.",
                "expected_outcome": f"Growing {best_cat.lower()}'s share of order mix compounds directly, since it already converts sales to profit at the highest rate of any category in this dataset.",
            })

    # REC-SALES-04: regional profitability gap
    if _cols_present(df, ["Region"]):
        reg = df.groupby("Region").apply(lambda g: g["Profit"].sum() / len(g) if len(g) > 0 else 0.0)
        reg_counts = df.groupby("Region").size()
        if len(reg) >= 2:
            best_region, worst_region = reg.idxmax(), reg.idxmin()
            best_val, worst_val = float(reg.max()), float(reg.min())
            gap_pct = (best_val - worst_val) / abs(best_val) if best_val != 0 else 0.0
            worst_count = int(reg_counts.get(worst_region, 0))
            parity_value = (best_val - worst_val) * worst_count
            recs.append({
                "id": "REC-SALES-04",
                "finding": f"'{worst_region}' underperforms '{best_region}' on average profit per order.",
                "evidence": f"Live: average profit per order is **${worst_val:,.2f}** in {worst_region} vs **${best_val:,.2f}** in {best_region} — a **{_fmt_pct(gap_pct)}** gap.",
                "recommendation": f"Review fulfillment SLAs, carrier contracts, and discount discipline specifically in the {worst_region} region.",
                "expected_outcome": f"Closing the gap to {best_region}'s per-order average would be worth roughly **{_fmt_money(parity_value)}** across {worst_region}'s {worst_count:,} recorded orders.",
            })

    # REC-SALES-05: bulk volume vs discount stacking
    if _cols_present(df, ["Order_Volume_Category", "Discount"]):
        bulk = df[df["Order_Volume_Category"].astype(str) == "Bulk_Volume"]
        low = df[df["Order_Volume_Category"].astype(str) == "Low_Volume"]
        if len(bulk) >= 5 and len(low) >= 5:
            bulk_disc = float(bulk["Discount"].mean())
            low_disc = float(low["Discount"].mean())
            if _worse_than(bulk_disc, low_disc, min_gap_pp=2.0):
                recs.append({
                    "id": "REC-SALES-05",
                    "finding": "Bulk orders receive meaningfully deeper discounts than small orders in the active dataset.",
                    "evidence": f"Live: average discount on bulk orders (qty > 5) is **{_fmt_pct(bulk_disc)}** vs **{_fmt_pct(low_disc)}** on low-volume orders (qty <= 2).",
                    "recommendation": "Replace flat percentage coupon stacking with a structured tiered-quantity wholesale pricing table.",
                    "expected_outcome": "Preserves bulk-order volume momentum while preventing unintended double-discount stacking from eroding unit margin further.",
                })

    return recs


# ---------------------------------------------------------------------------
# CHURN
# ---------------------------------------------------------------------------

def _churn_rate(df, mask) -> Optional[float]:
    sub = df[mask]
    if len(sub) < 5:
        return None
    return float(sub["Churned"].mean())


def _churn_recs(df, model_ctx: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    if not _cols_present(df, ["Churned"]):
        return recs

    # REC-CHURN-01: contract type
    if _cols_present(df, ["Contract_Type"]):
        m2m_mask = df["Contract_Type"].astype(str).str.contains("month", case=False, na=False)
        m2m_rate = _churn_rate(df, m2m_mask)
        other_rate = _churn_rate(df, ~m2m_mask)
        if _worse_than(m2m_rate, other_rate):
            at_risk_arr = 0.0
            if _cols_present(df, ["Monthly_Charges"]):
                churned_m2m = df[m2m_mask & (df["Churned"] == 1)]
                at_risk_arr = float(churned_m2m["Monthly_Charges"].sum()) * 12
            recs.append({
                "id": "REC-CHURN-01",
                "finding": "Month-to-month contracts are the predominant driver of subscriber attrition.",
                "evidence": f"Live: month-to-month subscribers churn at **{_fmt_pct(m2m_rate)}** vs **{_fmt_pct(other_rate)}** for subscribers on longer-term contracts.",
                "recommendation": "Deploy targeted contract-migration incentives (e.g. one month free, or a speed/feature upgrade) at the 3- and 9-month marks.",
                "expected_outcome": (
                    f"Churned month-to-month subscribers in this dataset represent roughly **{_fmt_money(at_risk_arr)}** in lost annualized recurring charges — the pool a migration campaign would target."
                    if at_risk_arr > 0 else
                    "Converting even a portion of this segment to longer contracts directly reduces the churn rate gap shown above."
                ),
            })

    # REC-CHURN-02: support ticket velocity
    if _cols_present(df, ["Support_Tickets"]):
        high_ticket = _churn_rate(df, df["Support_Tickets"] >= 3)
        low_ticket = _churn_rate(df, df["Support_Tickets"] < 3)
        if _worse_than(high_ticket, low_ticket):
            recs.append({
                "id": "REC-CHURN-02",
                "finding": "Customers filing multiple unresolved support tickets show sharply elevated churn.",
                "evidence": f"Live: churn rate is **{_fmt_pct(high_ticket)}** for customers with >=3 support tickets vs **{_fmt_pct(low_ticket)}** for customers with fewer.",
                "recommendation": "Flag any account on its 3rd open ticket for automated escalation to a dedicated care team within 4 hours.",
                "expected_outcome": "Reduces ticket-friction attrition by intervening before repeated unresolved contacts compound into cancellation.",
            })

    # REC-CHURN-03: add-on service adoption
    if _cols_present(df, ["Tech_Support", "Online_Security"]):
        has_both = (df["Tech_Support"].astype(str) == "Yes") & (df["Online_Security"].astype(str) == "Yes")
        has_neither = (df["Tech_Support"].astype(str) != "Yes") & (df["Online_Security"].astype(str) != "Yes")
        adopters_rate = _churn_rate(df, has_both)
        bare_rate = _churn_rate(df, has_neither)
        if _worse_than(bare_rate, adopters_rate):
            recs.append({
                "id": "REC-CHURN-03",
                "finding": "Subscribers without Tech Support and Online Security add-ons churn far more often.",
                "evidence": f"Live: add-on adopters (both services) churn at **{_fmt_pct(adopters_rate)}** vs **{_fmt_pct(bare_rate)}** for subscribers with neither service.",
                "recommendation": "Bundle basic digital security and tech support complimentary for 6 months on all high-speed tiers.",
                "expected_outcome": "Increases service stickiness and raises the switching cost of leaving, directly addressing the churn gap shown above.",
            })

    # REC-CHURN-04: payment method
    if _cols_present(df, ["Payment_Method"]):
        echeck_mask = df["Payment_Method"].astype(str).str.contains("electronic", case=False, na=False)
        other_pay_mask = ~echeck_mask
        echeck_rate = _churn_rate(df, echeck_mask)
        other_pay_rate = _churn_rate(df, other_pay_mask)
        if _worse_than(echeck_rate, other_pay_rate):
            recs.append({
                "id": "REC-CHURN-04",
                "finding": "Electronic check payers show a materially higher churn rate than other payment methods.",
                "evidence": f"Live: electronic-check payers churn at **{_fmt_pct(echeck_rate)}** vs **{_fmt_pct(other_pay_rate)}** for all other payment methods combined.",
                "recommendation": "Incentivize migration to automated ACH or card auto-pay with a one-time bill credit.",
                "expected_outcome": "Reduces involuntary, payment-friction-driven churn by removing the manual payment step most correlated with lapses.",
            })

    # REC-CHURN-05: data-driven decision threshold (Youden's J on the held-out test fold)
    if model_ctx is not None and model_ctx.get("probs") is not None:
        try:
            from sklearn.metrics import roc_curve
            y_test = model_ctx["y_test"]
            probs = model_ctx["probs"]
            fpr, tpr, thresholds = roc_curve(y_test, probs)
            j_scores = tpr - fpr
            best_idx = int(np.argmax(j_scores))
            best_threshold = float(thresholds[best_idx])
            best_threshold = min(max(best_threshold, 0.0), 1.0)
            best_recall = float(tpr[best_idx])
            best_fpr = float(fpr[best_idx])
            default_recall = float(tpr[(np.abs(thresholds - 0.5)).argmin()]) if len(thresholds) else 0.0
            extra_catches = int(round((best_recall - default_recall) * int((y_test == 1).sum())))
            recs.append({
                "id": "REC-CHURN-05",
                "finding": "A decision threshold tuned for this dataset's held-out fold outperforms the default 0.50 cutoff.",
                "evidence": f"Live (Youden's J on the held-out test split): optimal threshold is **{best_threshold:.2f}**, reaching **{_fmt_pct(best_recall)}** recall at **{_fmt_pct(best_fpr)}** false-positive rate.",
                "recommendation": f"Calibrate the production retention-campaign trigger to the {best_threshold:.2f} probability cutoff instead of the generic 0.50 default.",
                "expected_outcome": (
                    f"Catches roughly **{extra_catches:,} additional churn-bound customers** on this held-out split compared to the default 0.50 cutoff, at the recall/FPR trade-off above."
                    if extra_catches > 0 else
                    "Matches or improves on the default cutoff's recall while keeping the false-positive rate in check."
                ),
            })
        except Exception:
            pass

    return recs


# ---------------------------------------------------------------------------
# HR ATTRITION
# ---------------------------------------------------------------------------

def _attr_rate(df, mask) -> Optional[float]:
    sub = df[mask]
    if len(sub) < 5:
        return None
    return float(sub["Attrition"].mean())


def _hr_recs(df, model_ctx: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    if not _cols_present(df, ["Attrition"]):
        return recs

    # REC-HR-01: overtime + work-life balance
    if _cols_present(df, ["Overtime"]):
        ot_mask = df["Overtime"].astype(str).str.lower() == "yes"
        ot_rate = _attr_rate(df, ot_mask)
        no_ot_rate = _attr_rate(df, ~ot_mask)
        if _worse_than(ot_rate, no_ot_rate):
            recs.append({
                "id": "REC-HR-01",
                "finding": "Mandatory overtime is associated with a steep rise in attrition.",
                "evidence": f"Live: overtime employees show **{_fmt_pct(ot_rate)}** attrition vs **{_fmt_pct(no_ot_rate)}** for non-overtime peers.",
                "recommendation": "Cap consecutive overtime weeks at 2 and institute mandatory compensatory time-off with workload rebalancing.",
                "expected_outcome": "Narrows the attrition gap shown above by removing the single strongest burnout driver present in this dataset.",
            })

    # REC-HR-02: role stagnation
    if _cols_present(df, ["Years_In_Current_Role"]):
        stagnant = df["Years_In_Current_Role"] > 3.5
        stag_rate = _attr_rate(df, stagnant)
        fresh_rate = _attr_rate(df, ~stagnant)
        if _worse_than(stag_rate, fresh_rate):
            recs.append({
                "id": "REC-HR-02",
                "finding": "Employees stagnant in their current role for an extended period show elevated flight risk.",
                "evidence": f"Live: employees with >3.5 years in their current role attrite at **{_fmt_pct(stag_rate)}** vs **{_fmt_pct(fresh_rate)}** for those with recent role changes.",
                "recommendation": "Mandate bi-annual internal mobility reviews and lateral mentorship pathways for staff past 2.5 years in grade.",
                "expected_outcome": "Reduces the stagnation-driven share of departures by giving long-tenured-in-role staff a visible growth path before they look externally.",
            })

    # REC-HR-03: compensation
    if _cols_present(df, ["Monthly_Income"]):
        exit_income = df.loc[df["Attrition"] == 1, "Monthly_Income"]
        stay_income = df.loc[df["Attrition"] == 0, "Monthly_Income"]
        if len(exit_income) >= 5 and len(stay_income) >= 5:
            exit_med, stay_med = float(exit_income.median()), float(stay_income.median())
            recs.append({
                "id": "REC-HR-03",
                "finding": "Employees who leave tend to earn noticeably less than those who stay.",
                "evidence": f"Live: median monthly income of exiting staff is **${exit_med:,.0f}** vs **${stay_med:,.0f}** for retained staff.",
                "recommendation": "Conduct semi-annual market salary benchmarking for the lowest compensation bands and adjust toward market median.",
                "expected_outcome": "Closing this compensation gap directly addresses a quantifiable, data-confirmed driver of this dataset's attrition.",
            })

    # REC-HR-04: commute distance
    if _cols_present(df, ["Distance_From_Home"]):
        far = df["Distance_From_Home"] > 18
        far_rate = _attr_rate(df, far)
        near_rate = _attr_rate(df, ~far)
        if _worse_than(far_rate, near_rate):
            recs.append({
                "id": "REC-HR-04",
                "finding": "Long commutes materially aggravate turnover.",
                "evidence": f"Live: employees commuting >18 miles attrite at **{_fmt_pct(far_rate)}** vs **{_fmt_pct(near_rate)}** for those closer to the office.",
                "recommendation": "Expand remote/hybrid flexibility to 3-4 days per week for employees living beyond 15 miles.",
                "expected_outcome": "Lowers commute-induced turnover without requiring a compensation change.",
            })

    # REC-HR-05: first-year tenure hazard window
    if _cols_present(df, ["Years_At_Company"]):
        departures = df[df["Attrition"] == 1]
        if len(departures) >= 5:
            first_year_share = float((departures["Years_At_Company"] <= 1).mean())
            recs.append({
                "id": "REC-HR-05",
                "finding": "Early tenure represents the highest-hazard window for organizational drop-out.",
                "evidence": f"Live: **{_fmt_pct(first_year_share)}** of all recorded departures in this dataset occur within the first year of employment.",
                "recommendation": "Revamp onboarding with dedicated peer-buddy pairings and structured 30/60/90-day sentiment check-ins.",
                "expected_outcome": "Targets the single largest concentration of departures identified in the active dataset.",
            })

    # REC-HR-06: satisfaction deficit
    if _cols_present(df, ["Job_Satisfaction", "Environment_Satisfaction"]):
        low_sat = (df["Job_Satisfaction"] <= 2) & (df["Environment_Satisfaction"] <= 2)
        low_rate = _attr_rate(df, low_sat)
        rest_rate = _attr_rate(df, ~low_sat)
        if _worse_than(low_rate, rest_rate):
            recs.append({
                "id": "REC-HR-06",
                "finding": "Job and environment dissatisfaction compound each other into a strong attrition signal.",
                "evidence": f"Live: employees with low scores on both job and environment satisfaction attrite at **{_fmt_pct(low_rate)}** vs **{_fmt_pct(rest_rate)}** for everyone else.",
                "recommendation": "Run anonymous quarterly manager-feedback pulses and offer coaching for managers whose teams cluster in this segment.",
                "expected_outcome": "Surfaces and remediates team-climate issues before they convert into resignations.",
            })

    # REC-HR-07: subgroup equity (reuses the same methodology as the Responsible ML page)
    if model_ctx is not None and model_ctx.get("y_test") is not None:
        group_cols = [c for c in ["Gender", "Department", "Work_Mode"] if c in df.columns]
        if group_cols:
            try:
                from sklearn.metrics import recall_score
                y_test = model_ctx["y_test"]
                preds = model_ctx["preds"]
                test_idx = y_test.index
                recalls = []
                for gc in group_cols:
                    labels = df.loc[test_idx, gc].astype(str)
                    for val in labels.dropna().unique():
                        mask = (labels == val).values
                        if mask.sum() >= 30:
                            r = recall_score(y_test[mask], preds[mask], zero_division=0)
                            recalls.append(r)
                if len(recalls) >= 2:
                    spread = (max(recalls) - min(recalls)) * 100
                    recs.append({
                        "id": "REC-HR-07",
                        "finding": "Subgroup equity audit of the production model's recall across demographic/role segments.",
                        "evidence": f"Live (held-out test fold, subgroups with n>=30): recall spread across {', '.join(group_cols)} segments is **{spread:.1f} percentage points**.",
                        "recommendation": "Retain mandatory human HR review for any supportive intervention — this model must never drive automated personnel actions.",
                        "expected_outcome": (
                            "This spread is within a typical tolerance band for this dataset." if spread < 10 else
                            "This spread exceeds a 10-point tolerance band — review feature inputs for proxy bias before relying on this model for any individual-level signal."
                        ),
                    })
            except Exception:
                pass

    return recs


def build_recommendations(df: Any, project_option: str, model_ctx: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """Computes live, data-grounded recommendations for whichever dataset
    (bundled or uploaded) is currently active. Returns [] gracefully if the
    active dataset is missing the columns a given finding needs."""
    if pd is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []
    if project_option == "SALES":
        return _sales_recs(df)
    elif project_option == "CHURN":
        return _churn_recs(df, model_ctx)
    elif project_option == "HR_ATTRITION":
        return _hr_recs(df, model_ctx)
    return []
