from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.model import generate_saas_actuals
from src.forecasting import baseline_forecast


DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"


def ensure_outputs() -> None:
    """Create artifacts if they don't exist yet (first-run friendly)."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    fact_path = PROCESSED_DIR / "fact_finance_monthly.csv"
    forecast_path = PROCESSED_DIR / "forecast_outputs.csv"

    if not fact_path.exists():
        df = generate_saas_actuals(months=48, seed=7)
        df.to_csv(fact_path, index=False)

    if not forecast_path.exists():
        fact = pd.read_csv(fact_path, parse_dates=["month"])

        rev = baseline_forecast(fact, "revenue", horizon=24).pivot(index="month", columns="kind", values="revenue").reset_index()
        cash = baseline_forecast(fact, "ending_cash", horizon=24).pivot(index="month", columns="kind", values="ending_cash").reset_index()

        out = pd.merge(rev, cash, on="month", how="outer", suffixes=("_revenue", "_cash"))
        out = out.rename(
            columns={
                "actual_revenue": "revenue_actual",
                "forecast_revenue": "revenue_forecast",
                "actual_ending_cash": "ending_cash_actual",
                "forecast_ending_cash": "ending_cash_forecast",
            }
        )

        # pandas pivot creates columns 'actual'/'forecast' (not 'actual_revenue'); handle that
        if "actual" in out.columns and "forecast" in out.columns:
            # This would only happen if columns collide; ignore.
            pass

        out.to_csv(forecast_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, default=48)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    fact = generate_saas_actuals(months=args.months, seed=args.seed)
    fact.to_csv(PROCESSED_DIR / "fact_finance_monthly.csv", index=False)

    rev = baseline_forecast(fact, "revenue", horizon=24).pivot(index="month", columns="kind", values="revenue").reset_index()
    cash = baseline_forecast(fact, "ending_cash", horizon=24).pivot(index="month", columns="kind", values="ending_cash").reset_index()

    out = pd.merge(rev, cash, on="month", how="outer", suffixes=("_revenue", "_cash"))
    out = out.rename(
        columns={
            "actual_revenue": "revenue_actual",
            "forecast_revenue": "revenue_forecast",
            "actual_ending_cash": "ending_cash_actual",
            "forecast_ending_cash": "ending_cash_forecast",
        }
    )

    out.to_csv(PROCESSED_DIR / "forecast_outputs.csv", index=False)

    print("Wrote:")
    print("- data/processed/fact_finance_monthly.csv")
    print("- data/processed/forecast_outputs.csv")


if __name__ == "__main__":
    main()
