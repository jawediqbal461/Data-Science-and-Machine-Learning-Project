"""
tests/test_prediction.py
Unit tests for inference, loss warnings, risk bands, and threshold behavior.
"""

import unittest
from utils.prediction import (
    predict_sales_profit,
    predict_churn_probability,
    predict_hr_attrition,
    classify_profit,
    classify_churn_risk
)


class TestPredictionEngine(unittest.TestCase):

    def test_sales_profit_loss_warning(self):
        """Test high discount triggers negative profit and prominent loss warning."""
        loss_inputs = {
            "Sales": 100.0,
            "Discount": 0.45,  # High discount
            "Quantity": 1,
            "Shipping_Cost": 40.0,
            "Region": "South",
            "Category": "Furniture"
        }
        res = predict_sales_profit(loss_inputs)
        self.assertTrue(res["is_loss"])
        self.assertIsNotNone(res["loss_warning"])
        self.assertEqual(res["profit_category"], "Loss")

    def test_churn_threshold_recomputation(self):
        """Test threshold parameter adjusts classification without retraining."""
        inputs = {
            "Tenure_Months": 3,
            "Monthly_Charges": 95,
            "Contract_Type": "Month-to-month",
            "Support_Tickets": 4,
            "Complaints": 2,
            "Satisfaction_Score": 1
        }
        # At normal 0.50 threshold
        res_default = predict_churn_probability(inputs, threshold=0.50)
        prob = res_default["churn_probability"]

        # If we set threshold lower than prob
        res_low = predict_churn_probability(inputs, threshold=0.10)
        self.assertTrue(res_low["is_churn"])

        # If we set threshold higher than prob
        res_high = predict_churn_probability(inputs, threshold=0.99)
        self.assertFalse(res_high["is_churn"])

    def test_hr_attrition_mandatory_ethical_banner(self):
        """HR attrition prediction response must contain mandatory ethical banner."""
        inputs = {
            "Overtime": "Yes",
            "Work_Life_Balance": 1,
            "Job_Satisfaction": 1,
            "Monthly_Income": 2500,
            "Years_At_Company": 1,
            "Distance_From_Home": 25
        }
        res = predict_hr_attrition(inputs)
        self.assertIn("ethical_banner", res)
        self.assertIn("workforce-level analysis", res["ethical_banner"])
        self.assertIn("sole basis for termination", res["ethical_banner"])


if __name__ == "__main__":
    unittest.main()
