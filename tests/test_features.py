"""Checks that time-lagged predictors use past observations from the same country."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_data import build_features  # noqa: E402


class FeatureEngineeringTest(unittest.TestCase):
    def test_features_do_not_use_current_year(self):
        data = pd.DataFrame({
            "Country Name": ["Example"] * 5,
            "Year": [2000, 2001, 2002, 2003, 2004],
            "GDP_Growth": [1., 3., 5., 7., 9.],
            "Inflation": [10., 11., 12., 13., 14.],
            "Unemployment": [8., 7., 9., 8., 6.],
        })
        result = build_features(data)
        y2003 = result.loc[result["Year"] == 2003].iloc[0]
        self.assertEqual(y2003["GDP_Lag1"], 5.0)
        self.assertEqual(y2003["GDP_Rolling3"], 3.0)
        self.assertEqual(y2003["Inflation_Lag1"], 12.0)
        self.assertEqual(y2003["Unemployment_Change"], 2.0)

    def test_lags_are_grouped_by_country(self):
        data = pd.DataFrame({
            "Country Name": ["A", "A", "B", "B"],
            "Year": [2023, 2024, 2023, 2024],
            "GDP_Growth": [1., 2., 100., 200.],
            "Inflation": [3., 4., 5., 6.],
            "Unemployment": [8., 7., 6., 5.],
        })
        result = build_features(data)
        for country, expected in (("A", 1.), ("B", 100.)):
            row = result.loc[(result["Country Name"] == country) & (result["Year"] == 2024)].iloc[0]
            self.assertEqual(row["GDP_Lag1"], expected)


if __name__ == "__main__":
    unittest.main()
