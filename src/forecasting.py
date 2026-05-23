from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def baseline_forecast(df: pd.DataFrame, y_col: str, horizon: int = 24) -> pd.DataFrame:
    """Transparent baseline forecast using linear trend."""

    d = df.sort_values("month").copy()
    d = d[["month", y_col]].dropna()
    d["t"] = np.arange(len(d))

    X = d[["t"]].values
    y = d[y_col].values

    model = LinearRegression()
    model.fit(X, y)

    future = pd.DataFrame({"t": np.arange(len(d), len(d) + horizon)})
    future["month"] = pd.date_range(start=d["month"].max() + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    future[y_col] = model.predict(future[["t"]].values)

    return pd.concat(
        [
            d[["month", y_col]].assign(kind="actual"),
            future[["month", y_col]].assign(kind="forecast"),
        ],
        ignore_index=True,
    )
