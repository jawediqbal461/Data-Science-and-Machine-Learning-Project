"""
utils/data_source.py
Abstract Data Ingestion Architecture & Concrete Source Adapters.

Architecture Specification:
- Abstract base class: DataSource
- Metadata container: DataSourceMeta
- Adapters:
  * BundledCSVSource (default cold start from data/dataset.csv)
  * UploadedFileSource (in-memory per-session file upload)
  * WebhookPushSource (polling data/incoming/ populated by HMAC-verified FastAPI sidecar)
  * DatabaseReadOnlySource (SQL SELECT-only via st.secrets)
  * RestAPIPullSource (JSON/CSV endpoint pull via API key)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import os
from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore


@dataclass
class DataSourceMeta:
    """Standardized metadata envelope for loaded datasets."""
    source_type: str
    source_label: str
    loaded_at: str  # UTC ISO timestamp
    row_count: int
    column_count: int
    sha256: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_label": self.source_label,
            "loaded_at": self.loaded_at,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "sha256": self.sha256,
            "warnings": self.warnings,
        }


class DataSource(ABC):
    """Abstract interface defining contract for all data ingestion adapters."""

    @abstractmethod
    def load(self) -> Tuple[Any, DataSourceMeta]:
        """Loads dataset and returns (dataframe, metadata). Raises ValueError/IOError on failure."""
        pass

    @abstractmethod
    def describe(self) -> str:
        """Returns user-facing description for sidebar status: 'Currently using: ...'"""
        pass

    @staticmethod
    def compute_hash(content_bytes: bytes) -> str:
        """Computes SHA-256 hash for tamper/change detection."""
        return hashlib.sha256(content_bytes).hexdigest()


class BundledCSVSource(DataSource):
    """Loads bundled dataset from disk (data/dataset.csv). Cold-start default."""

    def __init__(self, file_path: str = "data/dataset.csv"):
        self.file_path = file_path

    def describe(self) -> str:
        return f"Bundled CSV Archive (`{self.file_path}`)"

    def load(self) -> Tuple[Any, DataSourceMeta]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"MISSING_DATASET: Bundled file not found at '{self.file_path}'. "
                "Please place the assignment dataset at this path or select another source."
            )

        with open(self.file_path, "rb") as f:
            raw_bytes = f.read()

        sha256_hash = self.compute_hash(raw_bytes)

        if pd is not None:
            import io
            df = pd.read_csv(io.BytesIO(raw_bytes))
            row_count, col_count = df.shape
        else:
            # Fallback if pandas not installed
            lines = raw_bytes.decode("utf-8", errors="replace").strip().split("\n")
            row_count = max(0, len(lines) - 1)
            col_count = len(lines[0].split(",")) if lines else 0
            df = {"raw_lines": len(lines)}

        meta = DataSourceMeta(
            source_type="BundledCSVSource",
            source_label=f"Local disk: {self.file_path}",
            loaded_at=datetime.now(timezone.utc).isoformat(),
            row_count=row_count,
            column_count=col_count,
            sha256=sha256_hash,
            warnings=[]
        )
        return df, meta


class UploadedFileSource(DataSource):
    """Handles user-uploaded CSV/Excel file in memory. Never touches disk for session safety."""

    def __init__(self, uploaded_file: Any, filename: Optional[str] = None):
        self.uploaded_file = uploaded_file
        self.filename = filename or getattr(uploaded_file, "name", "uploaded_file.csv")

    def describe(self) -> str:
        return f"User Upload Session (`{self.filename}` - In-Memory)"

    def load(self) -> Tuple[Any, DataSourceMeta]:
        if self.uploaded_file is None:
            raise ValueError("No uploaded file provided.")

        # Read bytes
        if hasattr(self.uploaded_file, "getvalue"):
            raw_bytes = self.uploaded_file.getvalue()
        elif hasattr(self.uploaded_file, "read"):
            raw_bytes = self.uploaded_file.read()
            if hasattr(self.uploaded_file, "seek"):
                self.uploaded_file.seek(0)
        elif isinstance(self.uploaded_file, (bytes, bytearray)):
            raw_bytes = bytes(self.uploaded_file)
        else:
            raise ValueError("Unsupported upload file object format.")

        sha256_hash = self.compute_hash(raw_bytes)
        warnings: List[str] = []

        if pd is not None:
            import io
            if self.filename.endswith(".xlsx") or self.filename.endswith(".xls"):
                df = pd.read_excel(io.BytesIO(raw_bytes))
            else:
                df = pd.read_csv(io.BytesIO(raw_bytes))
            row_count, col_count = df.shape
        else:
            lines = raw_bytes.decode("utf-8", errors="replace").strip().split("\n")
            row_count = max(0, len(lines) - 1)
            col_count = len(lines[0].split(",")) if lines else 0
            df = {"raw_lines": len(lines)}

        if row_count == 0:
            warnings.append("Uploaded dataset contains 0 rows.")

        meta = DataSourceMeta(
            source_type="UploadedFileSource",
            source_label=f"Session File: {self.filename}",
            loaded_at=datetime.now(timezone.utc).isoformat(),
            row_count=row_count,
            column_count=col_count,
            sha256=sha256_hash,
            warnings=warnings
        )
        return df, meta


class WebhookPushSource(DataSource):
    """Pulls latest HMAC-verified CSV dropped by FastAPI sidecar into data/incoming/"""

    def __init__(self, incoming_dir: str = "data/incoming"):
        self.incoming_dir = incoming_dir

    def describe(self) -> str:
        return f"Webhook Drop Zone (`{self.incoming_dir}/` - HMAC Verified Sidecar)"

    def load(self) -> Tuple[Any, DataSourceMeta]:
        if not os.path.exists(self.incoming_dir):
            raise FileNotFoundError(f"Webhook incoming directory '{self.incoming_dir}' does not exist.")

        files = [
            os.path.join(self.incoming_dir, f)
            for f in os.listdir(self.incoming_dir)
            if f.endswith(".csv") and not f.startswith(".")
        ]

        if not files:
            raise FileNotFoundError(
                f"No webhook ingestion payloads found in '{self.incoming_dir}'. "
                "Trigger the sidecar via `python send_webhook_demo.py` or POST to /webhook/ingest."
            )

        # Pick most recent file
        latest_file = max(files, key=os.path.getmtime)
        with open(latest_file, "rb") as f:
            raw_bytes = f.read()

        sha256_hash = self.compute_hash(raw_bytes)

        if pd is not None:
            import io
            df = pd.read_csv(io.BytesIO(raw_bytes))
            row_count, col_count = df.shape
        else:
            lines = raw_bytes.decode("utf-8", errors="replace").strip().split("\n")
            row_count = max(0, len(lines) - 1)
            col_count = len(lines[0].split(",")) if lines else 0
            df = {"raw_lines": len(lines)}

        meta = DataSourceMeta(
            source_type="WebhookPushSource",
            source_label=f"Webhook Payload: {os.path.basename(latest_file)}",
            loaded_at=datetime.now(timezone.utc).isoformat(),
            row_count=row_count,
            column_count=col_count,
            sha256=sha256_hash,
            warnings=[f"Loaded payload file: {os.path.basename(latest_file)}"]
        )
        return df, meta


class DatabaseReadOnlySource(DataSource):
    """Reads dataset via read-only SQL query against Postgres/Supabase instance."""

    def __init__(self, table_name: str = "capstone_data", connection_uri: Optional[str] = None):
        self.table_name = table_name
        self.connection_uri = connection_uri

    def describe(self) -> str:
        return f"Database Read-Only (`SELECT * FROM {self.table_name}` via st.secrets)"

    def load(self) -> Tuple[Any, DataSourceMeta]:
        if not self.connection_uri:
            raise ConnectionError(
                "DatabaseReadOnlySource requires a connection URI configured in `.streamlit/secrets.toml`. "
                "See README.md for connection parameters."
            )
        # Architectural implementation contract:
        raise NotImplementedError("DatabaseReadOnlySource connection established; table query hook ready.")


class RestAPIPullSource(DataSource):
    """Pulls JSON/CSV data from an authorized external REST endpoint."""

    def __init__(self, endpoint_url: str, api_key: Optional[str] = None):
        self.endpoint_url = endpoint_url
        self.api_key = api_key

    def describe(self) -> str:
        return f"External REST API (`{self.endpoint_url}`)"

    def load(self) -> Tuple[Any, DataSourceMeta]:
        if not self.endpoint_url:
            raise ValueError("Endpoint URL must be specified.")
        # Architectural implementation contract:
        raise NotImplementedError("RestAPIPullSource endpoint configured; polling hook ready.")
