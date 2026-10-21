"""
send_webhook_demo.py
Demonstration script for viva defense: simulates an external transactional pipeline
sending signed streaming data batches to the FastAPI webhook sidecar.

Usage:
    python send_webhook_demo.py
"""

import hashlib
import hmac
import os
import sys

# Sample batch CSV payload
SAMPLE_CSV_PAYLOAD = """Order_ID,Customer_ID,Customer_Name,Order_Date,Region,Category,Sub_Category,Sales,Quantity,Discount,Shipping_Cost,Ship_Mode,Profit,Customer_Rating,Returned,Total_Sale
ORD-9001,CUST-501,Alice Johnson,2026-10-15,West,Technology,Phones,650.00,2,0.05,25.00,Second Class,145.20,4.8,0,650.00
ORD-9002,CUST-502,Bob Smith,2026-10-16,East,Office Supplies,Paper,45.50,5,0.00,5.50,Standard Class,12.30,4.2,0,45.50
ORD-9003,CUST-503,Carol White,2026-10-17,Central,Furniture,Chairs,320.00,1,0.25,35.00,Standard Class,-18.40,3.5,0,320.00
ORD-9004,CUST-504,David Brown,2026-10-18,South,Technology,Accessories,180.00,3,0.10,12.00,First Class,42.10,4.9,0,180.00
"""

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "super-secret-capstone-key-2026")
ENDPOINT_URL = "http://localhost:8000/webhook/ingest"


def generate_signature(payload_bytes: bytes, secret: str) -> str:
    """Generates HMAC-SHA256 hex digest for request header."""
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def main():
    payload_bytes = SAMPLE_CSV_PAYLOAD.strip().encode("utf-8")
    signature = generate_signature(payload_bytes, WEBHOOK_SECRET)

    print("=" * 65)
    print("CAPSTONE VIVA DEMO: WEBHOOK INGESTION CLIENT")
    print("=" * 65)
    print(f"Target Endpoint : {ENDPOINT_URL}")
    print(f"Payload Size    : {len(payload_bytes)} bytes (~4 rows)")
    print(f"HMAC-SHA256 Sig : {signature}")
    print("-" * 65)

    try:
        import requests
        headers = {
            "Content-Type": "text/csv",
            "X-Signature": signature
        }
        print("Sending POST request to sidecar...")
        resp = requests.post(ENDPOINT_URL, data=payload_bytes, headers=headers, timeout=5)
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body  : {resp.text}")
    except Exception as e:
        print(f"[NOTE] Webhook server not currently running at {ENDPOINT_URL} ({e}).")
        print("\nEquivalent cURL command for viva defense:")
        print("-" * 65)
        print(f"curl -X POST {ENDPOINT_URL} \\")
        print("  -H 'Content-Type: text/csv' \\")
        print(f"  -H 'X-Signature: {signature}' \\")
        print("  --data-binary @data/sample_batch.csv")
        print("-" * 65)


if __name__ == "__main__":
    main()
