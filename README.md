# FP&A SaaS Financial Planning Dashboard (Portfolio Project)

A portfolio-grade, end-to-end FP&A project designed for **Sr. Financial Analyst / FP&A Analyst** roles (Big Tech-style). It includes:

- A realistic **SaaS operating model** (customers, churn, ARPA, MRR/ARR)
- A clean **FP&A dataset** (P&L-style) generated from business drivers
- **Forecasting** (baseline) + **driver-based scenarios** (Bear/Base/Bull)
- A polished **Streamlit dashboard** for non-technical stakeholders

## Dashboard Preview (mock)
Below is a simple *layout mock* (not a real screenshot) to help non-technical reviewers quickly understand what the dashboard looks like.

![Dashboard preview mock](assets/dashboard_preview_mock.png)

> Tip: After you run the dashboard locally (or deploy it), replace this mock with 2–3 real screenshots (KPI row, scenario table, and trend charts).

## Executive summary (for non-technical reviewers)
This dashboard answers common FP&A questions:
- *If churn increases by 0.5%*, how does ARR and cash runway change?
- *If we invest in growth (more new customers)*, do we improve operating income or just burn more cash?
- *If cloud costs rise*, do we still hit margin targets?

Use the sidebar sliders to adjust assumptions and compare **Bear / Base / Bull** scenarios.

---

## Quickstart

```bash
# 1) Create environment (optional)
python -m venv .venv
source .venv/bin/activate  # mac/linux
# .venv\Scripts\activate   # windows

# 2) Install deps
pip install -r requirements.txt

# 3) Generate data + baseline forecast outputs
python -m src.pipeline --months 48 --seed 7

# 4) Launch dashboard
streamlit run app.py
```

---

## Outputs
After running the pipeline, you will get:

- `data/processed/fact_finance_monthly.csv` (core FP&A table)
- `data/processed/forecast_outputs.csv` (baseline forecast time series)

---

## What to screenshot for your portfolio
After you run the app, take screenshots of:
1. KPI row + Revenue chart
2. Scenario comparison table
3. Operating income / ending cash scenario lines

Then add them to the README under a **Dashboard Preview** section.

---

## Project structure

```
.
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 01_exploration.ipynb
└── src/
    ├── __init__.py
    ├── pipeline.py
    ├── model.py
    ├── forecasting.py
    └── viz.py
```

---

## Notes / assumptions
- Data is **synthetic but realistic**, built from a SaaS driver model.
- This is intentional: it avoids confidentiality issues while still demonstrating real FP&A skills.
