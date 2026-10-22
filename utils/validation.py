"""
utils/validation.py
Schema Gate & Data Quality Validation Engine.

Strictly enforces schema verification before any exploratory analysis or ML training.
Provides structured ValidationReport and column mapping suggestions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Canonical required feature columns per track, shared by app.py (schema
# gate) and utils/header.py (auto column-mapping on upload) so both stay
# in sync with a single source of truth.
REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "SALES": ["Sales", "Quantity", "Discount", "Shipping_Cost", "Region", "Category", "Sub_Category"],
    "CHURN": ["Tenure_Months", "Contract_Type", "Monthly_Charges", "Total_Charges", "Support_Tickets", "Complaints"],
    "HR_ATTRITION": ["Age", "Department", "Job_Role", "Monthly_Income", "Job_Level", "Years_At_Company", "Overtime", "Work_Life_Balance"],
}


import re
import difflib

# Common abbreviations seen in real-world spreadsheet/CSV exports, expanded
# before token comparison so e.g. "Order_Qty" matches canonical "Quantity"
# and "Disc_Pct" matches canonical "Discount". Generic (not dataset-specific)
# so it holds up against any uploaded file, not just the bundled samples.
_TOKEN_SYNONYMS = {
    "qty": "quantity", "amt": "amount", "pct": "percent", "pcnt": "percent",
    "disc": "discount", "desc": "description", "cust": "customer",
    "dept": "department", "yrs": "year", "yr": "year", "mo": "month",
    "mos": "month", "addr": "address", "num": "number", "no": "number",
    "id": "identifier", "ship": "shipping", "rev": "revenue", "sale": "sales",
    "amount": "sales", "sal": "salary", "ot": "overtime", "tix": "ticket",
    "tenure": "year",
}

# Generic/noisy words that appear in lots of unrelated column names ("Order
# Count", "Total Value", "Item Number"...). They're excluded from the
# token-overlap signal (so they can't manufacture a false match on their
# own) but still contribute to the difflib ratio and acronym checks.
_GENERIC_TOKENS = {"count", "number", "total", "value", "amount", "data", "info", "flag", "type", "code"}


def _stem(tok: str) -> str:
    # Light plural stemming so "Tickets" lines up with "Ticket_Count" etc.
    if len(tok) > 4 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 4 and tok.endswith("es") and not tok.endswith(("ses", "xes")):
        return tok[:-1]
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok


def _tokens(name: str) -> List[str]:
    # Split on separators and camelCase boundaries, lowercase, stem plurals,
    # expand known abbreviations (re-stemming the expansion too, since a
    # synonym's value can itself be a plural-ish word), drop empties.
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    raw = re.split(r"[_\-\s]+", spaced.lower())
    out = []
    for t in raw:
        if not t:
            continue
        t = _stem(t)
        t = _TOKEN_SYNONYMS.get(t, t)
        t = _stem(t)
        out.append(t)
    return out


def _normalize(name: str) -> str:
    return "".join(_tokens(name))


def _acronym(tokens: List[str]) -> str:
    return "".join(t[0] for t in tokens if t)


def suggest_column_mappings(existing_cols: List[str], expected_cols: List[str]) -> Dict[str, str]:
    """Fuzzy-matches each canonical expected column name to the closest
    uploaded column name using, in order of confidence: an exact match
    after normalization, token-set overlap (so "Order_Qty" matches
    "Quantity" and "Sale_Amount" matches "Sales" via the synonym table
    above), and finally a difflib similarity-ratio threshold as a general
    fallback for near-misspellings. Returns {canonical_name: uploaded_name}
    only for canonical columns that aren't already present verbatim and
    that have a plausible candidate. Used both by validate_dataset (to
    populate ValidationReport.suggested_mappings) and by render_header (to
    auto-apply the mapping the moment a dataset is uploaded, with no
    manual step required)."""
    suggestions: Dict[str, str] = {}
    used_candidates: set = set()
    for col in expected_cols:
        if col in existing_cols:
            continue
        clean_col = _normalize(col)
        col_tokens_list = _tokens(col)
        col_tokens = set(col_tokens_list)
        best, best_score = None, 0.0
        for cand in existing_cols:
            if cand in used_candidates:
                continue
            clean_cand = _normalize(cand)
            cand_tokens_list = _tokens(cand)
            cand_tokens = set(cand_tokens_list)

            if clean_cand == clean_col:
                best, best_score = cand, 1.0
                break

            score = 0.0
            col_sig = (col_tokens - _GENERIC_TOKENS) or col_tokens
            cand_sig = (cand_tokens - _GENERIC_TOKENS) or cand_tokens
            if col_sig and cand_sig:
                shared = col_sig & cand_sig
                if shared:
                    jaccard = len(shared) / len(col_sig | cand_sig)
                    containment = len(shared) / min(len(col_sig), len(cand_sig))
                    score = max(score, jaccard, containment * 0.85)
            if clean_cand in clean_col or clean_col in clean_cand:
                score = max(score, 0.75)
            # Acronym match: a single short candidate token spelling out the
            # initials of the canonical name's words (e.g. "WLB" <-> "Work
            # Life Balance"), or vice versa.
            if len(cand_tokens_list) == 1 and len(col_tokens_list) > 1 and cand_tokens_list[0] == _acronym(col_tokens_list):
                score = max(score, 0.85)
            if len(col_tokens_list) == 1 and len(cand_tokens_list) > 1 and col_tokens_list[0] == _acronym(cand_tokens_list):
                score = max(score, 0.85)
            score = max(score, difflib.SequenceMatcher(None, clean_cand, clean_col).ratio())

            if score > best_score:
                best, best_score = cand, score

        if best is not None and best_score >= 0.6:
            suggestions[col] = best
            used_candidates.add(best)
    return suggestions


@dataclass
class ColumnStatus:
    name: str
    required: bool
    is_target: bool
    status: str  # "PRESENT", "MISSING", "MAPPED"
    detected_dtype: Optional[str] = None
    missing_count: int = 0
    missing_pct: float = 0.0


@dataclass
class ValidationReport:
    is_valid: bool
    can_train_ml: bool
    schema_status: str  # "PASSED", "WARNINGS", "CRITICAL_MISSING"
    total_columns_required: int
    present_columns: List[str]
    missing_columns: List[str]
    unexpected_columns: List[str]
    column_table: List[ColumnStatus]
    target_column: str
    target_present: bool
    row_count: int
    duplicate_count: int
    summary_messages: List[str] = field(default_factory=list)
    suggested_mappings: Dict[str, str] = field(default_factory=dict)


def validate_dataset(
    df: Any,
    required_columns: List[str],
    target_column: str,
    column_mapping: Optional[Dict[str, str]] = None
) -> ValidationReport:
    """
    Validates any incoming DataFrame against the target schema and column mapping.
    
    Args:
        df: pandas DataFrame or dict
        required_columns: Expected feature and meta column names
        target_column: Prediction target column name
        column_mapping: Optional user-defined mapping {canonical_name: uploaded_column_name}
    """
    column_mapping = column_mapping or {}
    summary_messages: List[str] = []
    
    # Extract columns and row count
    if hasattr(df, "columns"):
        existing_cols = list(df.columns)
        row_count = len(df)
        try:
            duplicate_count = int(df.duplicated().sum())
        except Exception:
            duplicate_count = 0
    elif isinstance(df, dict) and "columns" in df:
        existing_cols = list(df["columns"])
        row_count = df.get("row_count", 0)
        duplicate_count = 0
    else:
        existing_cols = []
        row_count = 0
        duplicate_count = 0

    all_expected = list(set(required_columns + [target_column]))
    present_cols: List[str] = []
    missing_cols: List[str] = []
    column_table: List[ColumnStatus] = []
    suggested_mappings: Dict[str, str] = suggest_column_mappings(existing_cols, all_expected)

    target_present = False

    # Check each expected column
    for col in all_expected:
        is_target = (col == target_column)
        
        # Check direct presence
        if col in existing_cols:
            status = "PRESENT"
            present_cols.append(col)
            if is_target:
                target_present = True
            dtype = str(df[col].dtype) if hasattr(df, "columns") else "unknown"
            miss_count = int(df[col].isna().sum()) if hasattr(df, "columns") else 0
            miss_pct = round((miss_count / row_count * 100), 2) if row_count > 0 else 0.0
        # Check if mapped by user
        elif col in column_mapping and column_mapping[col] in existing_cols:
            status = "MAPPED"
            actual_col = column_mapping[col]
            present_cols.append(col)
            if is_target:
                target_present = True
            dtype = str(df[actual_col].dtype) if hasattr(df, "columns") else "unknown"
            miss_count = int(df[actual_col].isna().sum()) if hasattr(df, "columns") else 0
            miss_pct = round((miss_count / row_count * 100), 2) if row_count > 0 else 0.0
        else:
            status = "MISSING"
            missing_cols.append(col)
            dtype = None
            miss_count = row_count
            miss_pct = 100.0

        column_table.append(
            ColumnStatus(
                name=col,
                required=True,
                is_target=is_target,
                status=status,
                detected_dtype=dtype,
                missing_count=miss_count,
                missing_pct=miss_pct
            )
        )

    unexpected_cols = [c for c in existing_cols if c not in all_expected and c not in column_mapping.values()]

    if not target_present:
        summary_messages.append(
            f"CRITICAL: Target column '{target_column}' is missing from dataset. ML training & evaluation disabled."
        )

    if missing_cols:
        summary_messages.append(
            f"Schema Validation Notice: {len(missing_cols)} required column(s) missing: {', '.join(missing_cols)}. Use the Column-Mapping UI below to align dataset fields."
        )
    else:
        summary_messages.append("Schema check passed: All mandatory fields are present and aligned.")

    if duplicate_count > 0:
        summary_messages.append(f"Data Quality: Found {duplicate_count} duplicate rows (will be removed in preprocessing).")

    is_valid = len(missing_cols) == 0
    can_train_ml = is_valid and target_present

    schema_status = "PASSED" if is_valid else ("CRITICAL_MISSING" if not target_present else "WARNINGS")

    return ValidationReport(
        is_valid=is_valid,
        can_train_ml=can_train_ml,
        schema_status=schema_status,
        total_columns_required=len(all_expected),
        present_columns=present_cols,
        missing_columns=missing_cols,
        unexpected_columns=unexpected_cols,
        column_table=column_table,
        target_column=target_column,
        target_present=target_present,
        row_count=row_count,
        duplicate_count=duplicate_count,
        summary_messages=summary_messages,
        suggested_mappings=suggested_mappings,
    )
