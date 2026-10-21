"""
utils/data_loader.py
Session-safe data loader wrapper around active DataSource adapters.

Enforces session boundary rules:
- Bundled files are cached with @st.cache_data
- Uploaded files reside purely in memory (never written to disk)
- Webhook payloads are fetched fresh based on file modification timestamp
"""

from typing import Any, Dict, Optional, Tuple
from utils.data_source import (
    DataSource,
    DataSourceMeta,
    BundledCSVSource,
    UploadedFileSource,
    WebhookPushSource,
    DatabaseReadOnlySource,
    RestAPIPullSource,
)

# Global or cache registry
_SOURCE_REGISTRY: Dict[str, DataSource] = {}


def get_adapter(source_key: str, **kwargs: Any) -> DataSource:
    """Factory creating appropriate DataSource adapter instance."""
    if source_key == "bundled":
        path = kwargs.get("file_path", "data/dataset.csv")
        return BundledCSVSource(file_path=path)
    elif source_key == "upload":
        file_obj = kwargs.get("uploaded_file")
        filename = kwargs.get("filename")
        return UploadedFileSource(uploaded_file=file_obj, filename=filename)
    elif source_key == "webhook":
        incoming_dir = kwargs.get("incoming_dir", "data/incoming")
        return WebhookPushSource(incoming_dir=incoming_dir)
    elif source_key == "database":
        table = kwargs.get("table_name", "capstone_data")
        uri = kwargs.get("connection_uri")
        return DatabaseReadOnlySource(table_name=table, connection_uri=uri)
    elif source_key == "api":
        url = kwargs.get("endpoint_url", "https://api.example.com/v1/data")
        key = kwargs.get("api_key")
        return RestAPIPullSource(endpoint_url=url, api_key=key)
    else:
        raise ValueError(f"Unknown data source key: {source_key}")


def load_dataset_from_source(source: DataSource) -> Tuple[Any, DataSourceMeta]:
    """Loads dataset from the designated source."""
    return source.load()
