"""
tests/test_preprocessing.py
Unit tests for data preprocessing and feature engineering specifications.
"""

import unittest
from utils.feature_engineering import FEATURE_CATALOG
from utils.preprocessing import EXCLUSION_RULES, run_missing_value_strategies


class TestPreprocessingAndFeatures(unittest.TestCase):

    def test_feature_engineering_counts(self):
        """Verify that engineered features meet minimum requirements (>=5 for Sales/Churn, >=8 for HR)."""
        sales_features = FEATURE_CATALOG.get("SALES", [])
        churn_features = FEATURE_CATALOG.get("CHURN", [])
        hr_features = FEATURE_CATALOG.get("HR_ATTRITION", [])

        self.assertGreaterEqual(len(sales_features), 5, "Sales must have >= 5 engineered features")
        self.assertGreaterEqual(len(churn_features), 5, "Churn must have >= 5 engineered features")
        self.assertGreaterEqual(len(hr_features), 8, "HR must have >= 8 engineered features")

    def test_leakage_exclusion_rules(self):
        """Ensure ID columns and post-completion columns are excluded from features."""
        for track, rules in EXCLUSION_RULES.items():
            self.assertIn("id_cols", rules)
            self.assertTrue(len(rules["id_cols"]) > 0)
            self.assertIn("target", rules)

        # Specifically check Sales post-completion leakage
        sales_leakage = EXCLUSION_RULES["SALES"]["post_completion_leakage"]
        self.assertIn("Customer_Rating", sales_leakage)
        self.assertIn("Returned", sales_leakage)
        self.assertIn("Total_Sale", sales_leakage)

    def test_hr_missing_value_strategies_all_four(self):
        """Ensure all 4 missing value imputation strategies are computed for HR Attrition."""
        strategies = run_missing_value_strategies(None)
        expected_keys = ["row_drop", "mean", "median", "mode"]
        for key in expected_keys:
            self.assertIn(key, strategies)
            self.assertIn("f1_score", strategies[key])
            self.assertIn("recall", strategies[key])


if __name__ == "__main__":
    unittest.main()
