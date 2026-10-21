"""
utils/validation.py
Schema Gate & Data Quality Validation Engine.

Strictly enforces schema verification before any exploratory analysis or ML training.
Provides structured ValidationReport and column mapping suggestions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


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
    suggested_mappings: Dict[str, str] = {}

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

            # Generate smart fuzzy mapping suggestion if similar column exists
            for cand in existing_cols:
                clean_cand = cand.lower().replace("_", "").replace(" ", "")
                clean_col = col.lower().replace("_", "").replace(" ", "")
                if clean_cand == clean_col or clean_cand in clean_col or clean_col in clean_cand:
                    suggested_mappings[col] = cand
                    break

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
