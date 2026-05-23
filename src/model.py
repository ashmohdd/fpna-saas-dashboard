"""Synthetic SaaS operating model + driver-based scenario planning."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_month_start(dt: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=dt.year, month=dt.month, day=1)


def generate_saas_actuals(months: int = 48, seed: int = 7) -> pd.DataFrame:
    """Generate a realistic synthetic SaaS dataset at monthly grain."""

    rng = np.random.default_rng(seed)
    start = _to_month_start(pd.Timestamp.today() - pd.DateOffset(months=months - 1))
    month_index = pd.date_range(start=start, periods=months, freq="MS")

    # --- Core drivers ---
    cust = 1200
    base_new = 85
    base_churn_rate = 0.020  # monthly
    arpa = 240.0  # monthly avg revenue per account

    cloud_cogs_pct = 0.20
    support_cogs_pct = 0.07

    headcount = 45
    fully_loaded_cost = 14500.0  # per employee per month

    sales_marketing_base = 180_000.0
    rnd_base = 210_000.0
    gna_base = 95_000.0

    cash = 6_000_000.0

    rows = []
    for i, m in enumerate(month_index):
        seasonal = 1.0 + 0.10 * np.sin(2 * np.pi * (i % 12) / 12.0)
        new = max(0, int(rng.normal(base_new * seasonal, 10)))

        churn_rate = float(np.clip(rng.normal(base_churn_rate, 0.004), 0.005, 0.05))
        churn = int(round(cust * churn_rate))
        cust_next = max(0, cust + new - churn)

        arpa = arpa * (1.0 + rng.normal(0.002, 0.002))

        mrr = cust_next * arpa
        one_time = max(0.0, rng.normal(25_000, 12_000))
        revenue = mrr + one_time

        cloud_cogs = revenue * cloud_cogs_pct * (1.0 + rng.normal(0.0, 0.03))
        support_cogs = revenue * support_cogs_pct * (1.0 + rng.normal(0.0, 0.03))
        cogs = cloud_cogs + support_cogs
        gross_profit = revenue - cogs
        gross_margin_pct = gross_profit / revenue if revenue else 0.0

        if i % 6 == 0 and i > 0:
            headcount += int(np.clip(rng.normal(3, 2), -1, 7))
            headcount = max(25, headcount)

        payroll = headcount * fully_loaded_cost

        sales_marketing = sales_marketing_base * (1.0 + rng.normal(0.01, 0.05))
        rnd = rnd_base * (1.0 + rng.normal(0.01, 0.04))
        gna = gna_base * (1.0 + rng.normal(0.008, 0.03))

        opex = payroll + sales_marketing + rnd + gna
        operating_income = gross_profit - opex

        cash = cash + operating_income + rng.normal(20_000, 35_000)

        rows.append(
            {
                "month": m,
                "customers": cust_next,
                "new_customers": new,
                "churned_customers": churn,
                "churn_rate": churn / cust if cust else 0.0,
                "arpa": arpa,
                "mrr": mrr,
                "arr": mrr * 12.0,
                "one_time_revenue": one_time,
                "revenue": revenue,
                "cloud_cogs": cloud_cogs,
                "support_cogs": support_cogs,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin_pct": gross_margin_pct,
                "headcount": headcount,
                "payroll": payroll,
                "sales_marketing": sales_marketing,
                "rnd": rnd,
                "gna": gna,
                "opex": opex,
                "operating_income": operating_income,
                "ending_cash": cash,
            }
        )

        cust = cust_next

    df = pd.DataFrame(rows)
    burn = (-df["operating_income"]).clip(lower=0.0)
    df["runway_months"] = np.where(burn > 0, df["ending_cash"] / burn, np.nan)
    return df


def apply_driver_scenario(
    fact: pd.DataFrame,
    months_forward: int,
    growth_uplift: float,
    churn_delta: float,
    price_uplift: float,
    headcount_delta: int,
    cloud_cost_uplift: float,
    scenario_name: str,
) -> pd.DataFrame:
    """Project forward from last actual month using driver rules."""

    last = fact.sort_values("month").iloc[-1].to_dict()

    cust = int(last["customers"])
    base_new = float(fact.tail(6)["new_customers"].mean())
    base_churn_rate = float(fact.tail(6)["churn_rate"].mean())
    arpa = float(last["arpa"]) * (1.0 + price_uplift)

    headcount = int(last["headcount"]) + int(headcount_delta)

    fully_loaded_cost = float(last["payroll"]) / max(int(last["headcount"]), 1)

    sales_marketing = float(last["sales_marketing"]) * (1.0 + 0.40 * growth_uplift)
    rnd = float(last["rnd"]) * (1.0 + 0.15 * growth_uplift)
    gna = float(last["gna"]) * (1.0 + 0.05 * growth_uplift)

    cash = float(last["ending_cash"])

    start_month = pd.Timestamp(last["month"]) + pd.offsets.MonthBegin(1)
    months = pd.date_range(start=start_month, periods=months_forward, freq="MS")

    projected = []
    for _, m in enumerate(months):
        new = max(0, int(round(base_new * (1.0 + growth_uplift))))
        churn_rate = float(np.clip(base_churn_rate + churn_delta, 0.002, 0.08))
        churn = int(round(cust * churn_rate))
        cust = max(0, cust + new - churn)

        arpa = arpa * 1.002

        mrr = cust * arpa
        one_time = float(last["one_time_revenue"])
        revenue = mrr + one_time

        cloud_pct = float(last["cloud_cogs"] / max(last["revenue"], 1.0)) * (1.0 + cloud_cost_uplift)
        support_pct = float(last["support_cogs"] / max(last["revenue"], 1.0))

        cloud_cogs = revenue * cloud_pct
        support_cogs = revenue * support_pct
        cogs = cloud_cogs + support_cogs

        gross_profit = revenue - cogs
        gross_margin_pct = gross_profit / revenue if revenue else 0.0

        payroll = headcount * fully_loaded_cost
        opex = payroll + sales_marketing + rnd + gna
        operating_income = gross_profit - opex

        cash = cash + operating_income

        projected.append(
            {
                "month": m,
                "scenario": scenario_name,
                "customers": cust,
                "new_customers": new,
                "churned_customers": churn,
                "churn_rate": churn_rate,
                "arpa": arpa,
                "mrr": mrr,
                "arr": mrr * 12.0,
                "one_time_revenue": one_time,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin_pct": gross_margin_pct,
                "headcount": headcount,
                "opex": opex,
                "operating_income": operating_income,
                "ending_cash": cash,
            }
        )

    proj = pd.DataFrame(projected)
    burn = (-proj["operating_income"]).clip(lower=0.0)
    proj["runway_months"] = np.where(burn > 0, proj["ending_cash"] / burn, np.nan)
    return proj


def run_scenario_grid(
    fact: pd.DataFrame,
    months_forward: int,
    growth_uplift: float,
    churn_delta: float,
    price_uplift: float,
    headcount_delta: int,
    cloud_cost_uplift: float,
) -> pd.DataFrame:
    base = apply_driver_scenario(
        fact,
        months_forward,
        growth_uplift=growth_uplift,
        churn_delta=churn_delta,
        price_uplift=price_uplift,
        headcount_delta=headcount_delta,
        cloud_cost_uplift=cloud_cost_uplift,
        scenario_name="Base",
    )

    bear = apply_driver_scenario(
        fact,
        months_forward,
        growth_uplift=growth_uplift - 0.08,
        churn_delta=churn_delta + 0.008,
        price_uplift=price_uplift - 0.03,
        headcount_delta=headcount_delta + 3,
        cloud_cost_uplift=cloud_cost_uplift + 0.05,
        scenario_name="Bear",
    )

    bull = apply_driver_scenario(
        fact,
        months_forward,
        growth_uplift=growth_uplift + 0.08,
        churn_delta=churn_delta - 0.006,
        price_uplift=price_uplift + 0.04,
        headcount_delta=headcount_delta - 2,
        cloud_cost_uplift=cloud_cost_uplift - 0.03,
        scenario_name="Bull",
    )

    return pd.concat([bear, base, bull], ignore_index=True).sort_values(["scenario", "month"])
