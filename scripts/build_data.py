"""Prepare economic panel data, evaluate models, and export the 2026 scenario table.

Usage: python scripts/build_data.py
Input: data/raw/API_Download_DS2_EN_csv_v2_146823_LIST.csv
Outputs: data/processed/*.csv
"""

from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data/raw/API_Download_DS2_EN_csv_v2_146823_LIST.csv"
OUT = ROOT / "data/processed"
INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "GDP_Growth",
    "FP.CPI.TOTL.ZG": "Inflation",
    "SL.UEM.TOTL.ZS": "Unemployment",
}
FEATURES = ["GDP_Lag1", "GDP_Rolling3", "Inflation_Lag1", "Unemployment_Change"]
FOLDS = [(2010, 2011, 2013), (2013, 2014, 2016), (2016, 2017, 2019)]


def metric_row(name: str, actual: pd.Series, predicted) -> dict:
    return {
        "Model": name,
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "R2": r2_score(actual, predicted),
    }


def load_source() -> pd.DataFrame:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {RAW_FILE}\n"
            "Copy the original World Bank CSV into data/raw/ without renaming it."
        )
    df = pd.read_csv(RAW_FILE, skiprows=4)
    required = {"Country Name", "Country Code", "Indicator Name", "Indicator Code", "Year", "Value"}
    if not required.issubset(df.columns):
        missing = required.difference(df.columns)
        raise ValueError(f"Input schema is missing columns: {sorted(missing)}")
    df = df[list(required)].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna(subset=["Country Name", "Year", "Indicator Code"])
    df["Year"] = df["Year"].astype(int)
    df = df[df["Indicator Code"].isin(INDICATORS) & df["Year"].between(1990, 2025)]
    if df.empty:
        raise ValueError("No observations found for the expected indicators between 1990 and 2025.")
    # Stop if the source has multiple conflicting values for a country, year and indicator.
    dup = df.duplicated(["Country Name", "Year", "Indicator Code"], keep=False)
    if dup.any():
        raise ValueError("Duplicate country/year/indicator rows found. Check the original CSV.")
    df["Data_Status"] = np.where(df["Value"].notna(), "Available", "Missing")
    return df.sort_values(["Country Name", "Year", "Indicator Code"]).reset_index(drop=True)


def build_panel(clean: pd.DataFrame) -> pd.DataFrame:
    panel = clean.pivot(
        index=["Country Name", "Year"],
        columns="Indicator Code",
        values="Value",
    ).rename(columns=INDICATORS)
    # Keep country/year observations even when all indicator values are unavailable.
    panel = panel.reindex(columns=["GDP_Growth", "Inflation", "Unemployment"])
    panel = panel.reset_index().sort_values(["Country Name", "Year"]).reset_index(drop=True)
    panel.columns.name = None
    return panel


def build_features(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel.sort_values(["Country Name", "Year"]).copy()
    gdp = df.groupby("Country Name")["GDP_Growth"]
    infl = df.groupby("Country Name")["Inflation"]
    unemployment = df.groupby("Country Name")["Unemployment"]
    df["GDP_Lag1"] = gdp.shift(1)
    df["GDP_Rolling3"] = gdp.transform(lambda s: s.shift(1).rolling(3, min_periods=3).mean())
    df["Inflation_Lag1"] = infl.shift(1)
    df["Unemployment_Change"] = unemployment.transform(lambda s: s.diff().shift(1))
    return df


def evaluate(model_data: pd.DataFrame):
    train = model_data[model_data["Year"] <= 2019]
    test = model_data[model_data["Year"].between(2020, 2025)]
    if train.empty or test.empty:
        raise ValueError("Training and 2020–2025 test datasets must both contain complete rows.")
    x_train, y_train = train[FEATURES], train["GDP_Growth"]
    x_test, y_test = test[FEATURES], test["GDP_Growth"]
    lr = LinearRegression().fit(x_train, y_train)
    rf = RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=3,
                               random_state=42, n_jobs=-1).fit(x_train, y_train)
    tuned = RandomForestRegressor(n_estimators=200, max_depth=4, min_samples_leaf=5,
                                  random_state=42, n_jobs=-1).fit(x_train, y_train)
    rows = [metric_row("Previous-year baseline", y_test, test["GDP_Lag1"])]
    for name, model in (("Linear Regression", lr), ("Random Forest", rf),
                        ("Tuned Random Forest", tuned)):
        rows.append(metric_row(name, y_test, model.predict(x_test)))

    validation = []
    for train_end, start, end in FOLDS:
        training = model_data[model_data["Year"] <= train_end]
        checking = model_data[model_data["Year"].between(start, end)]
        if training.empty or checking.empty:
            continue
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(
                n_estimators=300, max_depth=6, min_samples_leaf=3,
                random_state=42, n_jobs=-1
            ),
            "Tuned Random Forest": RandomForestRegressor(
                n_estimators=200, max_depth=4, min_samples_leaf=5,
                random_state=42, n_jobs=-1
            ),
        }
        validation.append({"Period": f"{start}–{end}", "Model": "Previous-year baseline",
                           "MAE": mean_absolute_error(checking["GDP_Growth"], checking["GDP_Lag1"])})
        for name, model in models.items():
            model.fit(training[FEATURES], training["GDP_Growth"])
            val_pred = model.predict(checking[FEATURES])
            validation.append({"Period": f"{start}–{end}", "Model": name,
                               "MAE": mean_absolute_error(checking["GDP_Growth"], val_pred)})
    return pd.DataFrame(rows), pd.DataFrame(validation)


def forecast_2026(features_df: pd.DataFrame, model_data: pd.DataFrame):
    current = model_data[model_data["Year"] <= 2025]
    linear = LinearRegression().fit(current[FEATURES], current["GDP_Growth"])
    forest = RandomForestRegressor(
        n_estimators=200, max_depth=4, min_samples_leaf=5,
        random_state=42, n_jobs=-1
    ).fit(current[FEATURES], current["GDP_Growth"])
    forecasts = []
    excluded = []
    for country, group in features_df.groupby("Country Name"):
        years = group[group["Year"].isin([2023, 2024, 2025])].sort_values("Year")
        if years["Year"].tolist() != [2023, 2024, 2025]:
            excluded.append({"Country": country, "Reason": "Incomplete 2023–2025 history"})
            continue
        if years[["GDP_Growth", "Inflation", "Unemployment"]].isna().any().any():
            excluded.append({"Country": country, "Reason": "Missing recent indicators"})
            continue
        x_future = pd.DataFrame([{
            "GDP_Lag1": years.iloc[-1]["GDP_Growth"],
            "GDP_Rolling3": years["GDP_Growth"].mean(),
            "Inflation_Lag1": years.iloc[-1]["Inflation"],
            "Unemployment_Change": years.iloc[-1]["Unemployment"] - years.iloc[-2]["Unemployment"],
        }], columns=FEATURES)
        forecasts.append({
            "Country": country, "Year": 2026,
            "GDP_2025": float(years.iloc[-1]["GDP_Growth"]),
            "Linear_Regression": float(linear.predict(x_future)[0]),
            "Random_Forest": float(forest.predict(x_future)[0]),
        })
    if not forecasts:
        raise ValueError("No country has complete 2023–2025 input indicators for a 2026 estimate.")
    return (pd.DataFrame(forecasts).sort_values("Random_Forest", ascending=False),
            pd.DataFrame(excluded, columns=["Country", "Reason"]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    clean = load_source()
    panel = build_panel(clean)
    features_df = build_features(panel)
    model_data = features_df[["Country Name", "Year", *FEATURES, "GDP_Growth"]].dropna().copy()
    test_metrics, validation = evaluate(model_data)
    forecasts, excluded = forecast_2026(features_df, model_data)

    quality = pd.DataFrame({
        "Column": ["GDP_Growth", "Inflation", "Unemployment"],
        "Missing Values": [int(panel[c].isna().sum()) for c in ["GDP_Growth", "Inflation", "Unemployment"]],
        "Non-Missing Values": [int(panel[c].notna().sum()) for c in ["GDP_Growth", "Inflation", "Unemployment"]],
    })
    for filename, frame in {
        "economic_clean.csv": clean,
        "economic_pivot.csv": panel,
        "economic_features.csv": features_df,
        "economic_model_dataset.csv": model_data,
        "model_comparison.csv": test_metrics,
        "validation_results.csv": validation,
        "global_gdp_forecast_2026.csv": forecasts,
        "excluded_countries.csv": excluded,
        "data_quality_report.csv": quality,
    }.items():
        frame.to_csv(OUT / filename, index=False)
        print(f"Saved data/processed/{filename} ({len(frame):,} rows)")
    print(f"\nForecasts: {len(forecasts)} countries | Excluded: {len(excluded)}")
    print(forecasts[["Country", "Linear_Regression", "Random_Forest"]].round(3).to_string(index=False))
    print("\nExperimental research estimates; not official projections.")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
