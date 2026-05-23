from __future__ import annotations

import streamlit as st
import pandas as pd

from src.viz import kpi_row, line_chart
from src.model import run_scenario_grid
from src.pipeline import ensure_outputs


st.set_page_config(page_title="FP&A SaaS Dashboard", layout="wide")

st.title("FP&A SaaS Financial Planning Dashboard")
st.caption(
    "Portfolio project: forecasting + driver-based scenario planning for a SaaS business. "
    "Designed to be understandable for non-technical stakeholders."
)

# Ensure base artifacts exist (helpful for first run)
ensure_outputs()

fact = pd.read_csv("data/processed/fact_finance_monthly.csv", parse_dates=["month"])
forecast = pd.read_csv("data/processed/forecast_outputs.csv", parse_dates=["month"])

# -------------------- Sidebar controls --------------------
st.sidebar.header("Scenario drivers")
st.sidebar.caption("Adjust drivers and compare Bear/Base/Bull scenarios.")

months_forward = st.sidebar.slider("Months to project", min_value=12, max_value=36, value=24, step=6)

growth_uplift = st.sidebar.slider("New customer growth uplift", -0.20, 0.30, 0.05, step=0.01)
churn_delta = st.sidebar.slider("Churn delta (absolute)", -0.02, 0.03, 0.00, step=0.001)
price_uplift = st.sidebar.slider("ARPA uplift", -0.10, 0.20, 0.03, step=0.01)

headcount_delta = st.sidebar.slider("Headcount plan delta", -10, 30, 5, step=1)
cloud_cost_uplift = st.sidebar.slider("Cloud cost uplift", -0.10, 0.25, 0.05, step=0.01)

scenario = run_scenario_grid(
    fact=fact,
    months_forward=months_forward,
    growth_uplift=growth_uplift,
    churn_delta=churn_delta,
    price_uplift=price_uplift,
    headcount_delta=headcount_delta,
    cloud_cost_uplift=cloud_cost_uplift,
)

# -------------------- KPIs --------------------
st.subheader("Key KPIs")
base_last = scenario[scenario["scenario"] == "Base"].iloc[-1]

kpi_row(
    {
        "ARR": base_last["arr"],
        "Revenue": base_last["revenue"],
        "Gross Margin %": base_last["gross_margin_pct"],
        "OpEx": base_last["opex"],
        "Operating Income": base_last["operating_income"],
        "Ending Cash": base_last["ending_cash"],
        "Runway (months)": base_last["runway_months"],
    }
)

# -------------------- Actuals vs forecast --------------------
st.subheader("Actuals vs baseline forecast")
merged = pd.merge(
    forecast,
    fact[["month", "revenue", "ending_cash"]],
    on="month",
    how="left",
    suffixes=("_forecast", "_actual"),
)

colA, colB = st.columns(2)
with colA:
    st.plotly_chart(
        line_chart(
            merged,
            x="month",
            y_cols=["revenue_actual", "revenue_forecast"],
            title="Revenue: actual vs forecast",
            y_format="currency",
        ),
        use_container_width=True,
    )
with colB:
    st.plotly_chart(
        line_chart(
            merged,
            x="month",
            y_cols=["ending_cash_actual", "ending_cash_forecast"],
            title="Ending cash: actual vs forecast",
            y_format="currency",
        ),
        use_container_width=True,
    )

# -------------------- Scenario comparison --------------------
st.subheader("Scenario comparison (end of projection)")
end_table = (
    scenario.groupby("scenario", as_index=False)
    .tail(1)[
        [
            "scenario",
            "arr",
            "revenue",
            "gross_margin_pct",
            "opex",
            "operating_income",
            "ending_cash",
            "runway_months",
        ]
    ]
    .sort_values("scenario")
)

st.dataframe(end_table, hide_index=True, use_container_width=True)

st.subheader("Scenario trends")
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(
        line_chart(scenario, x="month", y_cols=["arr"], color="scenario", title="ARR", y_format="currency"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        line_chart(
            scenario,
            x="month",
            y_cols=["operating_income"],
            color="scenario",
            title="Operating income",
            y_format="currency",
        ),
        use_container_width=True,
    )
with col3:
    st.plotly_chart(
        line_chart(
            scenario,
            x="month",
            y_cols=["ending_cash"],
            color="scenario",
            title="Ending cash",
            y_format="currency",
        ),
        use_container_width=True,
    )

st.caption(
    "Tip: After running, add screenshots to the README to make this very easy for recruiters/hiring managers to scan."
)
