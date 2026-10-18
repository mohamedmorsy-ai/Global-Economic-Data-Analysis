"""Interactive dashboard for historical economic indicators and experimental GDP growth estimates.

Run locally with: python -m streamlit run app.py
The required CSV reports are produced by scripts/build_data.py.
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
REQUIRED = ("economic_pivot.csv", "global_gdp_forecast_2026.csv")
COLORS = {"growth": "#57BDFF", "linear": "#F4C36B", "forest": "#59D8BF"}

st.set_page_config(
    page_title="Global Economic Data Analysis & Forecasting",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {background: #0B1220; color: #E8EEF9;}
[data-testid="stSidebar"] {background-color: #121D31;}
[data-testid="stMetric"] {
    background: #152138; border: 1px solid #253550;
    border-radius: 15px; padding: 18px;
}
[data-testid="stMetricValue"] {color: #59D8BF;}
h1, h2, h3 {letter-spacing: -.5px;}
.block-container {padding-top: 2rem; max-width: 1400px;}
div.stButton button, div.stDownloadButton button {border-radius: 11px;}
</style>
""", unsafe_allow_html=True)


def chart_theme(fig: go.Figure, height: int = 430):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1220",
        plot_bgcolor="#111D31",
        height=height,
        font=dict(color="#DCE7F7"),
        margin=dict(l=24, r=24, t=55, b=25),
        hovermode="x unified",
    )
    return fig


@st.cache_data(show_spinner=False)
def load_data():
    files = {
        "history": pd.read_csv(DATA / REQUIRED[0]),
        "forecast": pd.read_csv(DATA / REQUIRED[1]),
    }
    optional = {
        "models": "model_comparison.csv",
        "validation": "validation_results.csv",
        "quality": "data_quality_report.csv",
        "excluded": "excluded_countries.csv",
    }
    for key, filename in optional.items():
        path = DATA / filename
        files[key] = pd.read_csv(path) if path.exists() else pd.DataFrame()
    return files


st.sidebar.markdown("## 🌍 Economic Outlook")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Compare Countries", "Model Performance", "Data Explorer"],
    label_visibility="collapsed",
)
st.sidebar.divider()

st.title("Global Economic Data Analysis & Forecasting")
st.caption("Historical economic indicators · Comparative analysis · GDP growth estimates")

missing = [f for f in REQUIRED if not (DATA / f).exists()]
if missing:
    st.warning("The dashboard data has not been exported yet.")
    st.markdown("""**To complete the setup**

1. Copy the original World Bank CSV to `data/raw/`.
2. Run `python scripts/build_data.py` in the project folder.
3. Refresh this page.

The published app also needs the generated `data/processed/*.csv` files committed to the repository.
""")
    st.code("python scripts/build_data.py", language="bash")
    st.stop()

try:
    data = load_data()
except (pd.errors.ParserError, ValueError, OSError) as exc:
    st.error(f"Unable to read the exported data files: {exc}")
    st.stop()

history = data["history"]
forecast = data["forecast"]
required_hist = {"Country Name", "Year", "GDP_Growth", "Inflation", "Unemployment"}
required_fc = {"Country", "Year", "Linear_Regression", "Random_Forest"}
if not required_hist.issubset(history.columns) or not required_fc.issubset(forecast.columns):
    st.error("Dataset columns do not match the expected economic panel and forecast tables.")
    st.stop()

for field in ["Year", "GDP_Growth", "Inflation", "Unemployment"]:
    history[field] = pd.to_numeric(history[field], errors="coerce")
for field in ["Year", "GDP_2025", "Linear_Regression", "Random_Forest"]:
    if field in forecast.columns:
        forecast[field] = pd.to_numeric(forecast[field], errors="coerce")

countries = sorted(history["Country Name"].dropna().unique().tolist())
if not countries:
    st.error("The historical dataset does not contain any countries.")
    st.stop()
default_country = countries.index("Egypt, Arab Rep.") if "Egypt, Arab Rep." in countries else 0
selected = st.sidebar.selectbox("Country", countries, index=default_country)
st.sidebar.caption("Historical scope: 1990–2025")
st.sidebar.caption("Forecast horizon: 2026")
st.sidebar.caption("Research estimates, not official projections")

hist_one = history.loc[history["Country Name"] == selected].sort_values("Year")
fc_one = forecast.loc[forecast["Country"] == selected]
st.info(
    "2026 values are experimental model estimates derived from the provided historical dataset. "
    "Economic conditions and revisions to 2025 inputs may change the results."
)

if page == "Overview":
    st.subheader(f"Economic overview · {selected}")
    last = hist_one.loc[hist_one["Year"] == 2025, "GDP_Growth"]
    value_2025 = float(last.iloc[0]) if len(last) and pd.notna(last.iloc[0]) else None
    kpi = st.columns(4)
    kpi[0].metric("GDP growth · 2025", f"{value_2025:.2f}%" if value_2025 is not None else "N/A")
    kpi[1].metric("Linear regression · 2026", f"{fc_one.iloc[0]['Linear_Regression']:.2f}%" if len(fc_one) else "N/A")
    kpi[2].metric("Random forest · 2026", f"{fc_one.iloc[0]['Random_Forest']:.2f}%" if len(fc_one) else "N/A")
    kpi[3].metric("Observed GDP years", str(hist_one["GDP_Growth"].notna().sum()))
    if not len(fc_one):
        st.warning("A 2026 estimate is unavailable because recent required indicators are missing.")

    st.markdown("### GDP growth · Historical performance and 2026 estimates")
    fig = go.Figure()
    actual = hist_one.dropna(subset=["GDP_Growth"])
    fig.add_trace(go.Scatter(
        x=actual["Year"], y=actual["GDP_Growth"], mode="lines+markers",
        marker=dict(size=4), line=dict(color=COLORS["growth"], width=2),
        name="Historical GDP growth",
    ))
    if len(fc_one):
        latest_actual = actual.loc[actual["Year"] == 2025, "GDP_Growth"]
        if len(latest_actual):
            latest_growth = float(latest_actual.iloc[0])
            for col, name, color in [
                ("Linear_Regression", "Linear regression estimate", COLORS["linear"]),
                ("Random_Forest", "Random forest estimate", COLORS["forest"]),
            ]:
                fig.add_trace(go.Scatter(
                    x=[2025, 2026], y=[latest_growth, float(fc_one.iloc[0][col])],
                    mode="lines+markers", name=name,
                    line=dict(dash="dash", color=color, width=3),
                ))
    fig.update_xaxes(title="Year", dtick=5)
    fig.update_yaxes(title="Annual GDP growth (%)")
    st.plotly_chart(chart_theme(fig, 460), use_container_width=True)

    left, right = st.columns(2)
    for target, field, title, color in [
        (left, "Inflation", "Inflation (%)", COLORS["linear"]),
        (right, "Unemployment", "Unemployment (%)", COLORS["forest"]),
    ]:
        with target:
            indicator_plot = px.line(hist_one, x="Year", y=field, title=title, markers=True)
            indicator_plot.update_traces(line=dict(color=color), marker=dict(size=4))
            st.plotly_chart(chart_theme(indicator_plot, 350), use_container_width=True)

    st.markdown("### Global growth estimates · 2026")
    ranking = forecast.dropna(subset=["Random_Forest"]).sort_values("Random_Forest")
    if len(ranking):
        rank_chart = px.bar(
            ranking, x="Random_Forest", y="Country", orientation="h",
            labels={"Random_Forest": "Estimated GDP growth (%)", "Country": ""},
            color_discrete_sequence=[COLORS["forest"]],
        )
        st.plotly_chart(chart_theme(rank_chart, max(460, 31 * len(ranking))), use_container_width=True)

elif page == "Compare Countries":
    st.subheader("Compare countries")
    defaults = [c for c in ["Egypt, Arab Rep.", "China", "United States", "Germany"] if c in countries]
    selected_countries = st.multiselect("Choose countries", countries, default=defaults, max_selections=8)
    indicator = st.selectbox(
        "Economic indicator", ["GDP_Growth", "Inflation", "Unemployment"],
        format_func=lambda key: {"GDP_Growth": "GDP growth (%)", "Inflation": "Inflation (%)", "Unemployment": "Unemployment (%)"}[key],
    )
    if selected_countries:
        compare = history.loc[history["Country Name"].isin(selected_countries)]
        chart = px.line(compare, x="Year", y=indicator, color="Country Name", markers=False)
        chart.update_yaxes(title=indicator.replace("_", " ") + " (%)")
        st.plotly_chart(chart_theme(chart, 510), use_container_width=True)
        st.markdown("#### 2026 model estimates")
        st.dataframe(
            forecast.loc[forecast["Country"].isin(selected_countries)].round(3),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("Select at least one country.")

elif page == "Model Performance":
    st.subheader("Model performance")
    st.write(
        "Models were evaluated on historical periods, including a 2020–2025 test period. "
        "Because those test results were reviewed during development, treat them as diagnostic, "
        "not as a fully independent final benchmark."
    )
    metrics = data["models"]
    if not metrics.empty:
        st.markdown("#### Model comparison · 2020–2025")
        st.dataframe(metrics.round(4), use_container_width=True, hide_index=True)
        if {"Model", "MAE"}.issubset(metrics):
            plot = px.bar(metrics, x="Model", y="MAE", color_discrete_sequence=[COLORS["forest"]])
            plot.update_yaxes(title="Mean absolute error (percentage points)")
            st.plotly_chart(chart_theme(plot, 390), use_container_width=True)
    else:
        st.info("Model evaluation file not found. Run the preparation script to generate it.")
    validation = data["validation"]
    if not validation.empty:
        st.markdown("#### Walk-forward validation")
        st.dataframe(validation.round(4), use_container_width=True, hide_index=True)
        if {"Period", "Model", "MAE"}.issubset(validation):
            plot = px.bar(validation, x="Period", y="MAE", color="Model", barmode="group")
            plot.update_yaxes(title="MAE (percentage points)")
            st.plotly_chart(chart_theme(plot, 400), use_container_width=True)
    st.caption(
        "Forecast error differs by country and time. Large macroeconomic shocks can lead to sizable misses; "
        "no statistical prediction here should be interpreted as a guaranteed outcome."
    )

else:
    st.subheader("Data explorer")
    m = st.columns(3)
    m[0].metric("Countries in dataset", history["Country Name"].nunique())
    m[1].metric("Country-year rows", f"{len(history):,}")
    m[2].metric("Countries with estimates", forecast["Country"].nunique())
    minimum, maximum = int(history["Year"].min()), int(history["Year"].max())
    years = st.slider("Historical year range", minimum, maximum, (minimum, maximum))
    subset = hist_one.loc[hist_one["Year"].between(*years)]
    st.dataframe(subset.round(3), hide_index=True, use_container_width=True)
    st.download_button(
        "Download selected country data", subset.to_csv(index=False),
        file_name="country_history.csv", mime="text/csv",
    )
    if not data["quality"].empty:
        st.markdown("#### Missing observations by indicator")
        st.dataframe(data["quality"], use_container_width=True, hide_index=True)
    if not data["excluded"].empty:
        st.markdown("#### Countries without a complete 2026 estimate")
        st.dataframe(data["excluded"], hide_index=True, use_container_width=True)
    st.markdown("#### 2026 model estimates")
    st.dataframe(forecast.round(3), hide_index=True, use_container_width=True)
    st.download_button(
        "Download 2026 estimates", forecast.to_csv(index=False),
        file_name="global_gdp_forecast_2026.csv", mime="text/csv",
    )

st.divider()
st.caption(
    "Historical economic indicators sourced from the supplied World Bank-format CSV. "
    "2026 outputs are experimental one-year-ahead estimates, not official economic forecasts."
)
