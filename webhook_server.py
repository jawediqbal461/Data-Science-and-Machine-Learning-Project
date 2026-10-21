"""
webhook_server.py
Standalone FastAPI Webhook Ingestion Sidecar.

Runs independently on port 8000.
Enforces HMAC-SHA256 signature verification via X-Signature header.
Saves authenticated payload CSVs into data/incoming/<uuid>.csv.
"""

from datetime import datetime, timezone
import hashlib
import hmac
import os
import uuid
from typing import Dict, Any

try:
    from fastapi import FastAPI, Header, HTTPException, Request, Response, status
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    FastAPI = None  # type: ignore

app = FastAPI(
    title="Capstone Data Ingestion Webhook Sidecar",
    version="1.0.0",
    description="Secure HMAC-SHA256 authenticated ingest endpoint for stream data."
) if FastAPI is not None else None

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "super-secret-capstone-key-2026")
INCOMING_DIR = os.environ.get("INCOMING_DIR", "data/incoming")


def verify_hmac_signature(body_bytes: bytes, signature_header: str) -> bool:
    """Verifies HMAC-SHA256 signature against WEBHOOK_SECRET."""
    if not signature_header:
        return False
    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature_header.strip())


if app is not None:
    @app.get("/webhook/health")
    def health_check() -> Dict[str, Any]:
        """Uptime and status check endpoint."""
        return {
            "status": "healthy",
            "service": "webhook_sidecar",
            "port": 8000,
            "secret_configured": bool(WEBHOOK_SECRET),
            "incoming_dir": INCOMING_DIR,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @app.post("/webhook/ingest")
    async def ingest_webhook(
        request: Request,
        x_signature: str = Header(None, alias="X-Signature")
    ) -> Dict[str, Any]:
        """
        Receives CSV stream payload, verifies HMAC signature, and writes to data/incoming/<uuid>.csv.
        """
        body_bytes = await request.body()
        if not body_bytes:
            raise HTTPException(status_code=400, detail="Empty request body.")

        if not x_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing mandatory 'X-Signature' header. Unsigned payloads are rejected."
            )

        if not verify_hmac_signature(body_bytes, x_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid HMAC-SHA256 signature. Verification failed."
            )

        os.makedirs(INCOMING_DIR, exist_ok=True)
        file_id = str(uuid.uuid4())
        dest_filename = f"{file_id}.csv"
        dest_path = os.path.join(INCOMING_DIR, dest_filename)

        with open(dest_path, "wb") as f:
            f.write(body_bytes)

        # Parse row count
        lines = body_bytes.decode("utf-8", errors="replace").strip().split("\n")
        row_count = max(0, len(lines) - 1)
        sha256_hash = hashlib.sha256(body_bytes).hexdigest()

        return {
            "id": file_id,
            "status": "ACCEPTED",
            "received_at": datetime.now(timezone.utc).isoformat(),
            "saved_as": dest_filename,
            "row_count": row_count,
            "sha256": sha256_hash,
            "message": f"Successfully ingested {row_count} rows into {dest_path}."
        }


if __name__ == "__main__":
    if uvicorn is not None and app is not None:
        print(f"Starting Webhook Ingestion Server on port 8000 (Secret={WEBHOOK_SECRET[:4]}***)...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("FastAPI / Uvicorn not installed. Install via `pip install fastapi uvicorn` to run.")
