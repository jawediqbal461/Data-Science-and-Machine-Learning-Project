"""
tests/test_validation.py
Unit tests for data schema gate and validation engine.
"""

import unittest
from utils.validation import validate_dataset, ValidationReport


class TestValidationEngine(unittest.TestCase):

    def setUp(self):
        self.required_cols = ["Sales", "Quantity", "Discount", "Shipping_Cost"]
        self.target_col = "Profit"

    def test_complete_valid_schema(self):
        """Test dataset containing all required columns and target passes validation."""
        data = {
            "columns": ["Order_ID", "Sales", "Quantity", "Discount", "Shipping_Cost", "Profit"],
            "row_count": 100
        }
        report = validate_dataset(data, self.required_cols, self.target_col)
        self.assertTrue(report.is_valid)
        self.assertTrue(report.can_train_ml)
        self.assertEqual(report.schema_status, "PASSED")
        self.assertEqual(len(report.missing_columns), 0)

    def test_missing_target_disables_ml(self):
        """Test missing target column correctly disables ML training."""
        data = {
            "columns": ["Sales", "Quantity", "Discount", "Shipping_Cost"],
            "row_count": 50
        }
        report = validate_dataset(data, self.required_cols, self.target_col)
        self.assertFalse(report.can_train_ml)
        self.assertFalse(report.target_present)
        self.assertIn("Profit", report.missing_columns)
        self.assertEqual(report.schema_status, "CRITICAL_MISSING")

    def test_column_mapping_resolution(self):
        """Test user column mapping resolves mismatched column names."""
        data = {
            "columns": ["Rev_Sales", "Quantity", "Discount", "Shipping_Cost", "Net_Profit"],
            "row_count": 30
        }
        mapping = {
            "Sales": "Rev_Sales",
            "Profit": "Net_Profit"
        }
        report = validate_dataset(data, self.required_cols, self.target_col, column_mapping=mapping)
        self.assertTrue(report.is_valid)
        self.assertTrue(report.can_train_ml)
        self.assertEqual(report.schema_status, "PASSED")


if __name__ == "__main__":
    unittest.main()
