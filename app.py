"""Global Economic Data Analysis & Forecasting — Interactive dashboard.

This dashboard reads pre-generated CSV reports from data/processed/.
Run it locally with: streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# 01. Application settings and data paths
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"
REQUIRED_FILES = {
    "history": "economic_pivot.csv",
    "forecast": "global_gdp_forecast_2026.csv",
}
OPTIONAL_FILES = {
    "models": "model_comparison.csv",
    "validation": "validation_results.csv",
    "quality": "data_quality_report.csv",
    "excluded": "excluded_countries.csv",
}

PALETTE = {
    "navy": "#14243B",
    "slate": "#53647B",
    "blue": "#2563EB",
    "sky": "#60A5FA",
    "teal": "#0D9488",
    "amber": "#D97706",
    "border": "#E3EAF3",
    "background": "#F5F8FC",
    "white": "#FFFFFF",
}

st.set_page_config(
    page_title="Global Economic Data Analysis & Forecasting",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# 02. Professional light design
# ------------------------------------------------------------
st.markdown(
    """
<style>
:root { color-scheme: light; }
.stApp, [data-testid="stAppViewContainer"] {
  background-color: #F5F8FC !important;
  color: #14243B !important;
}
[data-testid="stHeader"] { background: rgba(245,248,252,.92) !important; }
.main .block-container, [data-testid="stMainBlockContainer"] {
  max-width: 1450px !important;
  padding-top: 2.4rem !important;
  padding-bottom: 3rem !important;
}
section[data-testid="stSidebar"], [data-testid="stSidebar"] {
  background: #FFFFFF !important;
  border-right: 1px solid #E3EAF3 !important;
}
[data-testid="stSidebar"] * { color: #14243B; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label { color: #53647B !important; }
[data-testid="stSidebar"] [role="radiogroup"] label {
  border-radius: 10px; padding: .5rem .65rem;
  margin: .17rem 0; color: #14243B !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #F1F5FC; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: #FFFFFF !important; border-color: #CBD5E1 !important;
  color: #14243B !important; border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #14243B !important; }
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  color: #14243B !important;
  letter-spacing: -.035em;
}
h1 { font-size: clamp(2rem, 3.5vw, 2.8rem) !important; font-weight: 780 !important; }
h2 { font-weight: 760 !important; }
h3 { font-weight: 700 !important; }
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
  color: #53647B;
}
[data-testid="stMetric"] {
  background: #FFFFFF !important;
  border: 1px solid #E3EAF3 !important;
  border-radius: 16px !important;
  padding: 1.2rem 1.3rem !important;
  min-height: 116px;
  box-shadow: 0 6px 22px rgba(28,51,85,.045) !important;
}
[data-testid="stMetricLabel"] *, [data-testid="stMetricLabel"] {
  color: #63758C !important; font-weight: 600 !important;
}
[data-testid="stMetricValue"] *, [data-testid="stMetricValue"] {
  color: #14243B !important; font-weight: 760 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] {
  border-color: #E3EAF3 !important;
  border-radius: 16px !important;
}
[data-testid="stAlert"] {
  background: #EEF5FF !important;
  border: 1px solid #CEE1FC !important;
  border-radius: 12px !important;
}
[data-testid="stAlert"] *, [data-testid="stAlert"] p { color: #1C497F !important; }
[data-testid="stDataFrame"] {
  border: 1px solid #E3EAF3 !important;
  border-radius: 12px !important;
  overflow: hidden;
}
.stButton > button, .stDownloadButton > button {
  border-radius: 10px !important; border: 1px solid #C9DBF6 !important;
  background: #FFFFFF !important; color: #1D4ED8 !important;
  font-weight: 650 !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: #EFF6FF !important; border-color: #2563EB !important;
}
[data-baseweb="select"] > div, [data-baseweb="input"] input {
  background: #FFFFFF !important; color: #14243B !important;
}
[data-testid="stSlider"] * { color: #14243B; }
hr { border-color: #E3EAF3 !important; }
.hero {
  background: linear-gradient(110deg,#FFFFFF 0%,#F0F6FF 100%);
  border: 1px solid #E0EAF9;
  border-radius: 20px;
  padding: 1.5rem 1.8rem 1.3rem;
  margin: 0 0 1.1rem;
  box-shadow: 0 5px 25px rgba(35,64,105,.04);
}
.hero-kicker { font-size: .74rem; font-weight: 750; letter-spacing: .17em; color: #2563EB; }
.hero-title {
  margin: .5rem 0 .5rem !important; font-size: clamp(1.65rem,3vw,2.55rem);
  line-height: 1.16; font-weight: 780; color: #14243B;
}
.hero-subtitle { color: #53647B; font-size: .95rem; margin: 0; }
.section-kicker {
  font-size: .76rem; text-transform: uppercase; letter-spacing: .12em;
  color: #2563EB; font-weight: 800; margin: 1.3rem 0 .25rem;
}
.small-note { color: #64748B; font-size: .81rem; line-height: 1.5; }
.sidebar-brand {
  font-size: 1.23rem; font-weight: 800; color: #14243B !important;
  letter-spacing: -.025em; margin-bottom: .22rem;
}
.sidebar-subtitle { font-size: .79rem; color: #64748B; margin-bottom: 1.35rem; }
footer { visibility: hidden; }
@media (max-width: 767px) {
 .main .block-container, [data-testid="stMainBlockContainer"] { padding: 1rem .7rem !important; }
 .hero { padding: 1.2rem; }
 [data-testid="stMetric"] { min-height: 100px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 03. Chart styling and reusable helpers
# ------------------------------------------------------------
def style_figure(fig: go.Figure, height: int = 420, *, hovermode: str = "x unified") -> go.Figure:
    """Apply consistent typography, axes and colors to every Plotly chart."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color=PALETTE["navy"], size=12),
        title_font=dict(size=17, color=PALETTE["navy"]),
        height=height,
        hovermode=hovermode,
        margin=dict(l=20, r=22, t=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(255,255,255,0)"),
        hoverlabel=dict(bgcolor="#FFFFFF", font=dict(color=PALETTE["navy"])),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EDF2F8", zerolinecolor="#D7E0EC", linecolor="#DFE7F0")
    fig.update_yaxes(showgrid=True, gridcolor="#EDF2F8", zerolinecolor="#D7E0EC", linecolor="#DFE7F0")
    return fig


def show_chart(fig: go.Figure, height: int = 420, *, hovermode: str = "x unified") -> None:
    st.plotly_chart(style_figure(fig, height, hovermode=hovermode), use_container_width=True, theme=None)


def section_heading(label: str, title: str, caption: str | None = None) -> None:
    st.markdown(f'<div class="section-kicker">{label}</div>', unsafe_allow_html=True)
    st.subheader(title)
    if caption:
        st.caption(caption)


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    result = {key: pd.read_csv(DATA_DIR / filename) for key, filename in REQUIRED_FILES.items()}
    for key, filename in OPTIONAL_FILES.items():
        path = DATA_DIR / filename
        result[key] = pd.read_csv(path) if path.exists() else pd.DataFrame()
    return result


# ------------------------------------------------------------
# 04. Sidebar and data validation
# ------------------------------------------------------------
st.sidebar.markdown(
    '<div class="sidebar-brand">🌐 Economic Outlook</div>'
    '<div class="sidebar-subtitle">Research dashboard · 1990—2026</div>',
    unsafe_allow_html=True,
)
page = st.sidebar.radio(
    "Pages",
    ["Overview", "Compare Countries", "Model Performance", "Data Explorer"],
)
st.sidebar.divider()

missing = [name for name in REQUIRED_FILES.values() if not (DATA_DIR / name).is_file()]
if missing:
    st.error("Required CSV reports were not found in data/processed/.")
    st.code("python scripts/build_data.py", language="bash")
    st.caption("Missing files: " + ", ".join(missing))
    st.stop()

try:
    data = load_data()
except (pd.errors.ParserError, ValueError, OSError) as exc:
    st.error(f"Could not read the project data files: {exc}")
    st.stop()

history, forecast = data["history"], data["forecast"]
required_history = {"Country Name", "Year", "GDP_Growth", "Inflation", "Unemployment"}
required_forecast = {"Country", "Year", "Linear_Regression", "Random_Forest"}
if not required_history.issubset(history.columns) or not required_forecast.issubset(forecast.columns):
    st.error("The uploaded CSV files are missing required columns. Re-run scripts/build_data.py.")
    st.stop()

for column in ["Year", "GDP_Growth", "Inflation", "Unemployment"]:
    history[column] = pd.to_numeric(history[column], errors="coerce")
for column in ["Year", "GDP_2025", "Linear_Regression", "Random_Forest"]:
    if column in forecast.columns:
        forecast[column] = pd.to_numeric(forecast[column], errors="coerce")

countries = sorted(history["Country Name"].dropna().unique().tolist())
if not countries:
    st.error("No countries are present in the historical dataset.")
    st.stop()

selected = st.sidebar.selectbox(
    "Select a country",
    countries,
    index=countries.index("Egypt, Arab Rep.") if "Egypt, Arab Rep." in countries else 0,
)
st.sidebar.markdown(
    '<div class="small-note">Historical data: 1990–2025<br>'
    'Forecast horizon: 2026<br><br>'
    'Experimental research estimates; not official projections.</div>',
    unsafe_allow_html=True,
)

selected_history = history.loc[history["Country Name"] == selected].sort_values("Year")
selected_forecast = forecast.loc[forecast["Country"] == selected]

st.markdown(
    '<div class="hero">'
    '<div class="hero-kicker">ECONOMIC RESEARCH & FORECASTING</div>'
    '<div class="hero-title">Global Economic Data Analysis & Forecasting</div>'
    '<p class="hero-subtitle">Explore historical economic indicators, compare countries, '
    'and review GDP growth estimates powered by statistical learning.</p>'
    '</div>',
    unsafe_allow_html=True,
)
st.info(
    "2026 values are experimental estimates, not verified or official forecasts. "
    "Model results depend on historical inputs, and 2025 data may be revised."
)

# ------------------------------------------------------------
# 05. Overview page — country snapshot and economic trends
# ------------------------------------------------------------
if page == "Overview":
    section_heading("01 / COUNTRY OVERVIEW", selected, "Historical indicators and illustrative 2026 model estimates")
    previous = selected_history.loc[selected_history["Year"] == 2025, "GDP_Growth"]
    previous_value = float(previous.iloc[0]) if not previous.empty and pd.notna(previous.iloc[0]) else None
    estimate = selected_forecast.iloc[0] if not selected_forecast.empty else None
    a, b, c, d = st.columns(4)
    a.metric("GDP Growth · 2025", f"{previous_value:.2f}%" if previous_value is not None else "N/A")
    b.metric("Linear Regression · 2026", f"{estimate['Linear_Regression']:.2f}%" if estimate is not None else "N/A")
    c.metric("Random Forest · 2026", f"{estimate['Random_Forest']:.2f}%" if estimate is not None else "N/A")
    d.metric("Years with GDP data", f"{selected_history['GDP_Growth'].notna().sum():,}")
    if estimate is None:
        st.warning("A 2026 estimate is unavailable because required 2023–2025 indicators are incomplete.")

    section_heading("ECONOMIC TRENDS", "GDP growth over time", "Historical values versus one-year-ahead estimates")
    fig = go.Figure()
    actual = selected_history.dropna(subset=["GDP_Growth"])
    fig.add_trace(go.Scatter(
        x=actual["Year"], y=actual["GDP_Growth"], mode="lines+markers",
        name="Historical GDP growth", line=dict(color=PALETTE["blue"], width=2.8),
        marker=dict(size=5, color=PALETTE["blue"]),
    ))
    if estimate is not None:
        final_actual = actual.loc[actual["Year"] == 2025, "GDP_Growth"]
        if not final_actual.empty:
            base_value = float(final_actual.iloc[0])
            for col, name, color in [
                ("Linear_Regression", "Linear regression · 2026", PALETTE["amber"]),
                ("Random_Forest", "Random forest · 2026", PALETTE["teal"]),
            ]:
                fig.add_trace(go.Scatter(
                    x=[2025, 2026], y=[base_value, float(estimate[col])],
                    name=name, mode="lines+markers",
                    line=dict(color=color, dash="dash", width=3), marker=dict(size=9),
                ))
    fig.update_xaxes(title="Year", dtick=5)
    fig.update_yaxes(title="Annual GDP growth (%)")
    show_chart(fig, 455)

    section_heading("KEY INDICATORS", "Inflation & unemployment")
    left, right = st.columns(2)
    for col, field, label, color in [
        (left, "Inflation", "Inflation rate (%)", PALETTE["amber"]),
        (right, "Unemployment", "Unemployment rate (%)", PALETTE["teal"]),
    ]:
        with col:
            chart = px.line(selected_history, x="Year", y=field, markers=True)
            chart.update_traces(line=dict(color=color, width=2.6), marker=dict(color=color, size=5))
            chart.update_xaxes(title="Year")
            chart.update_yaxes(title=label)
            show_chart(chart, 360)

    section_heading("GLOBAL OUTLOOK", "2026 GDP growth estimates", "Random Forest estimates ranked by country")
    ranked = forecast.dropna(subset=["Random_Forest"]).sort_values("Random_Forest")
    if not ranked.empty:
        bars = px.bar(
            ranked, x="Random_Forest", y="Country", orientation="h",
            labels={"Random_Forest": "Estimated GDP growth (%)", "Country": ""},
            color_discrete_sequence=[PALETTE["blue"]],
        )
        bars.update_traces(marker_line_width=0, hovertemplate="%{y}: %{x:.2f}%<extra></extra>")
        show_chart(bars, max(470, 30 * len(ranked)), hovermode="closest")

# ------------------------------------------------------------
# 06. Compare Countries page — historical trend comparisons
# ------------------------------------------------------------
elif page == "Compare Countries":
    section_heading("02 / COMPARATIVE ANALYSIS", "Compare countries", "Review economic patterns across selected countries")
    default_countries = [c for c in ["Egypt, Arab Rep.", "China", "United States", "Germany"] if c in countries]
    chosen = st.multiselect("Countries", countries, default=default_countries, max_selections=8)
    indicator_labels = {
        "GDP_Growth": "GDP growth (%)",
        "Inflation": "Inflation rate (%)",
        "Unemployment": "Unemployment rate (%)",
    }
    indicator = st.selectbox("Indicator", list(indicator_labels), format_func=lambda value: indicator_labels[value])
    if chosen:
        subset = history.loc[history["Country Name"].isin(chosen)].dropna(subset=[indicator])
        chart = px.line(
            subset, x="Year", y=indicator, color="Country Name",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        chart.update_xaxes(title="Year")
        chart.update_yaxes(title=indicator_labels[indicator])
        show_chart(chart, 520)
        section_heading("FORECAST COMPARISON", "2026 estimates")
        matching = forecast.loc[forecast["Country"].isin(chosen)]
        if matching.empty:
            st.info("No 2026 estimates are available for the selected countries.")
        else:
            st.dataframe(matching.round(3), use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one country to compare economic indicators.")

# ------------------------------------------------------------
# 07. Model Performance page — evaluation transparency
# ------------------------------------------------------------
elif page == "Model Performance":
    section_heading("03 / MACHINE LEARNING", "Model performance", "Error metrics and validation results")
    st.caption(
        "The 2020–2025 test period was reviewed during development; these metrics are diagnostic, "
        "not a fully independent estimate of future accuracy. Lower MAE and RMSE indicate smaller errors."
    )
    scores = data["models"]
    if not scores.empty:
        section_heading("EVALUATION", "Model comparison · 2020–2025")
        st.dataframe(scores.round(4), use_container_width=True, hide_index=True)
        if {"Model", "MAE"}.issubset(scores.columns):
            fig = px.bar(
                scores.sort_values("MAE"), x="Model", y="MAE",
                color_discrete_sequence=[PALETTE["blue"]],
                labels={"MAE": "Mean absolute error (percentage points)"},
                text_auto=".2f",
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            show_chart(fig, 380, hovermode="closest")
    else:
        st.info("The model comparison report is not available. Run scripts/build_data.py to generate it.")

    validation = data["validation"]
    if not validation.empty:
        section_heading("WALK-FORWARD", "Historical validation")
        st.dataframe(validation.round(4), use_container_width=True, hide_index=True)
        if {"Period", "Model", "MAE"}.issubset(validation.columns):
            fig = px.bar(
                validation, x="Period", y="MAE", color="Model", barmode="group",
                color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"], PALETTE["amber"], "#818CF8"],
                labels={"MAE": "MAE (percentage points)"},
            )
            show_chart(fig, 410, hovermode="closest")
    st.caption(
        "Forecast quality differs by country and time period. Economic disruptions, revisions "
        "and data coverage can affect predictions."
    )

# ------------------------------------------------------------
# 08. Data Explorer page — quality, filtering and CSV export
# ------------------------------------------------------------
else:
    section_heading("04 / DATA EXPLORER", "Explore the dataset", "Filter records and download the underlying tables")
    a, b, c = st.columns(3)
    a.metric("Countries", f"{history['Country Name'].nunique():,}")
    b.metric("Country–year records", f"{len(history):,}")
    c.metric("Countries with estimates", f"{forecast['Country'].nunique():,}")

    valid_years = history["Year"].dropna()
    if valid_years.empty:
        st.error("The dataset has no valid years.")
        st.stop()
    start, end = int(valid_years.min()), int(valid_years.max())
    years = st.slider("Historical year range", start, end, (start, end))
    filtered = selected_history.loc[selected_history["Year"].between(*years)]
    st.markdown("#### Selected country · Historical observations")
    st.dataframe(filtered.round(3), use_container_width=True, hide_index=True)
    st.download_button(
        "Download selected historical data",
        data=filtered.to_csv(index=False), file_name="country_history.csv", mime="text/csv",
    )

    if not data["quality"].empty:
        section_heading("DATA QUALITY", "Missing observations")
        st.dataframe(data["quality"], use_container_width=True, hide_index=True)
    if not data["excluded"].empty:
        section_heading("COVERAGE", "Countries without 2026 estimates")
        st.dataframe(data["excluded"], use_container_width=True, hide_index=True)

    section_heading("DOWNLOADS", "2026 GDP growth estimates")
    st.dataframe(forecast.round(3), use_container_width=True, hide_index=True)
    st.download_button(
        "Download forecast table (CSV)",
        data=forecast.to_csv(index=False),
        file_name="global_gdp_forecast_2026.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Data: supplied World Bank-format economic indicators. Forecasts for 2026 are experimental "
    "statistical estimates, not official projections."
)
