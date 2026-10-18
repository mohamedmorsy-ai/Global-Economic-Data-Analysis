# Global Economic Data Analysis & Forecasting

**Economic data analysis · Machine learning · GDP growth estimation**

An end-to-end Python project examining GDP growth, consumer-price inflation and unemployment across 20 economies between 1990 and 2025. It combines descriptive analysis, time-series feature engineering, machine-learning experiments and an interactive dashboard presenting illustrative estimates for 2026.

## Project highlights

- **Economic trends:** GDP growth, inflation and unemployment at country and year level.
- **Data quality:** explicit missing-value checks and country/indicator coverage.
- **Forecasting features:** prior-year growth, trailing three-year growth, prior-year inflation and lagged unemployment changes.
- **Model comparison:** previous-year baseline, linear regression and random forests.
- **Temporal evaluation:** walk-forward validation and a 2020–2025 diagnostic test period.
- **Interactive dashboard:** country profiles, comparisons, model diagnostics and downloadable tables.

## Tech stack

Python, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Plotly and Streamlit.

## Project structure

```text
Global-Economic-Data-Analysis/
├── app.py                           # Interactive Streamlit dashboard
├── requirements.txt                 # Python dependencies
├── .streamlit/config.toml           # Dashboard theme
├── notebooks/
│   └── Economic_Analysis.ipynb      # Annotated exploratory analysis and experiments
├── scripts/
│   └── build_data.py                # Reproducible preparation, evaluation and exports
└── data/
    ├── raw/                         # Original source CSV (not included)
    └── processed/                   # CSV outputs to publish with dashboard
```

## Data source and setup

The analysis expects an input CSV formatted as a World Bank indicator download, with the following fields:
`Country Name`, `Country Code`, `Indicator Name`, `Indicator Code`, `Year`, `Value`.

**The original source CSV is not included in this repository package.** Copy your original dataset to:

```text
data/raw/API_Download_DS2_EN_csv_v2_146823_LIST.csv
```

The three required indicator codes are:

| Indicator | World Bank code |
|---|---|
| GDP growth (annual %) | `NY.GDP.MKTP.KD.ZG` |
| Inflation, consumer prices (annual %) | `FP.CPI.TOTL.ZG` |
| Unemployment, total (% labor force) | `SL.UEM.TOTL.ZS` |

Some countries may not have complete observations for the final years, so they are not included in the 2026 estimates. Check the `excluded_countries.csv` output rather than filling unknown observations without justification.

## Run locally

```bash
# Run in the repository root (the folder containing app.py)
python -m pip install -r requirements.txt
python scripts/build_data.py
python -m streamlit run app.py
```

Open the local address displayed in your terminal, normally `http://localhost:8501`.

You can also open `notebooks/Economic_Analysis.ipynb` in Jupyter to follow the original analysis step by step. The Notebook can locate the raw dataset in `data/raw/` when started from the repository root or the `notebooks/` directory.

## Outputs

After running `build_data.py`, files are written under `data/processed/`:

| File | Description |
|---|---|
| `economic_clean.csv` | Clean long-form indicator records |
| `economic_pivot.csv` | Country-year historical panel |
| `economic_features.csv` | Time-lagged predictor columns |
| `economic_model_dataset.csv` | Complete cases used for modeling |
| `model_comparison.csv` | Historical evaluation statistics |
| `validation_results.csv` | Walk-forward validation MAE by model |
| `data_quality_report.csv` | Missing/available counts by indicator |
| `excluded_countries.csv` | Reasons some countries cannot be forecast |
| `global_gdp_forecast_2026.csv` | Experimental one-year-ahead GDP growth estimates |

These processed CSVs are required for the public dashboard. Generate them from your real dataset, inspect them, and commit them to GitHub alongside the app before deployment.

## Evaluation and interpretation

MAE and RMSE are expressed in **percentage points** of annual GDP growth. Model quality is not uniform across years or countries. Historic test results were inspected during development, so this project does not claim a fully untouched final benchmark. Prediction outputs for 2026 use historical inputs through 2025 and should be treated as **research estimates, not verified or official forecasts**. Source data may be revised.

## Publish the dashboard

1. Run the preprocessing script locally and confirm the charts and model results.
2. Commit `app.py`, `requirements.txt`, `.streamlit/config.toml`, the Notebook, and the generated `data/processed/` CSV files.
3. Push the repository to GitHub.
4. On [Streamlit Community Cloud](https://share.streamlit.io/), select the repository, branch `main`, and entry point `app.py`.
5. Deploy and open your resulting `https://...streamlit.app` URL.

No API tokens are needed for this local CSV-based version. Do not commit credentials, private datasets or `.streamlit/secrets.toml`.

## References

- [World Bank Data](https://data.worldbank.org/)
- [Scikit-learn](https://scikit-learn.org/stable/)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Pandas documentation](https://pandas.pydata.org/docs/)
