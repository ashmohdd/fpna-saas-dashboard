from __future__ import annotations

from typing import Dict, Optional

import pandas as pd
import plotly.express as px
import streamlit as st


def _fmt_currency(x: float) -> str:
    if pd.isna(x):
        return "—"
    sign = "-" if x < 0 else ""
    x = abs(float(x))
    if x >= 1_000_000:
        return f"{sign}${x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"{sign}${x/1_000:.1f}K"
    return f"{sign}${x:.0f}"


def _fmt_pct(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"{float(x)*100:.1f}%"


def kpi_row(values: Dict[str, float]) -> None:
    cols = st.columns(len(values))
    for (label, val), col in zip(values.items(), cols):
        if "%" in label:
            col.metric(label, _fmt_pct(val))
        elif "Runway" in label:
            col.metric(label, "∞" if pd.isna(val) else f"{val:.1f}")
        else:
            col.metric(label, _fmt_currency(val))


def line_chart(
    df: pd.DataFrame,
    x: str,
    y_cols: list[str],
    title: str,
    color: Optional[str] = None,
    y_format: str = "number",
):
    d = df.copy()

    if color is None and len(y_cols) > 1:
        d = d.melt(id_vars=[x], value_vars=y_cols, var_name="series", value_name="value")
        fig = px.line(d, x=x, y="value", color="series", title=title)
    elif color is not None and len(y_cols) == 1:
        fig = px.line(d, x=x, y=y_cols[0], color=color, title=title)
    else:
        fig = px.line(d, x=x, y=y_cols[0], title=title)

    if y_format == "currency":
        fig.update_yaxes(tickprefix="$", separatethousands=True)

    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), legend_title_text="")
    return fig
