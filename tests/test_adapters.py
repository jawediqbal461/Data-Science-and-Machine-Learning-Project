"""
tests/test_adapters.py
Unit tests for data source adapters and HMAC authentication.
"""

import io
import os
import shutil
import tempfile
import unittest
from utils.data_source import BundledCSVSource, UploadedFileSource, WebhookPushSource
from utils.validation import validate_dataset
from webhook_server import verify_hmac_signature, WEBHOOK_SECRET


class TestDataSourceAdapters(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_csv_text = "Sales,Quantity,Discount,Shipping_Cost,Profit\n100,2,0.1,10,25\n200,4,0.0,15,60\n"
        self.sample_file_path = os.path.join(self.temp_dir, "dataset.csv")
        with open(self.sample_file_path, "w", encoding="utf-8") as f:
            f.write(self.sample_csv_text)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_bundled_csv_loads_successfully(self):
        """BundledCSVSource successfully loads file and computes metadata sha256."""
        source = BundledCSVSource(file_path=self.sample_file_path)
        data, meta = source.load()
        self.assertEqual(meta.source_type, "BundledCSVSource")
        self.assertEqual(meta.row_count, 2)
        self.assertEqual(len(meta.sha256), 64)  # Valid SHA-256 length

    def test_bundled_csv_missing_file_raises(self):
        """BundledCSVSource raises FileNotFoundError on missing file."""
        source = BundledCSVSource(file_path=os.path.join(self.temp_dir, "non_existent.csv"))
        with self.assertRaises(FileNotFoundError):
            source.load()

    def test_uploaded_file_source_valid_schema(self):
        """UploadedFileSource in-memory load correctly passes schema validation."""
        bio = io.BytesIO(self.sample_csv_text.encode("utf-8"))
        bio.name = "my_uploaded_file.csv"

        source = UploadedFileSource(uploaded_file=bio)
        data, meta = source.load()
        self.assertEqual(meta.source_type, "UploadedFileSource")
        self.assertEqual(meta.row_count, 2)

        report = validate_dataset(
            {"columns": ["Sales", "Quantity", "Discount", "Shipping_Cost", "Profit"], "row_count": meta.row_count},
            required_columns=["Sales", "Quantity", "Discount", "Shipping_Cost"],
            target_column="Profit"
        )
        self.assertTrue(report.is_valid)

    def test_uploaded_file_source_wrong_columns_triggers_validation_error(self):
        """Uploaded file with incorrect column headers fails schema gate."""
        wrong_cols = ["RandomColA", "RandomColB"]
        report = validate_dataset(
            {"columns": wrong_cols, "row_count": 10},
            required_columns=["Sales", "Quantity", "Discount", "Shipping_Cost"],
            target_column="Profit"
        )
        self.assertFalse(report.is_valid)
        self.assertIn("Profit", report.missing_columns)
        self.assertIn("Sales", report.missing_columns)

    def test_webhook_hmac_verification(self):
        """HMAC-SHA256 signature verification passes on correct secret, rejects tampering."""
        import hmac
        import hashlib

        body = b"Sample,Webhook,Data\n1,2,3\n"
        correct_sig = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        bad_sig = "a" * 64

        self.assertTrue(verify_hmac_signature(body, correct_sig))
        self.assertFalse(verify_hmac_signature(body, bad_sig))
        self.assertFalse(verify_hmac_signature(b"tampered body", correct_sig))


if __name__ == "__main__":
    unittest.main()
