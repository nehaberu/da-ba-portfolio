# 📈 Data & Business Analyst Portfolio

Six self-contained, interview-ready projects covering the skills that show up in almost
every **Data Analyst / Business Analyst** job description: **SQL**, **Python analytics &
machine learning**, **BI dashboarding**, **A/B testing**, **data wrangling/ETL** and
**Excel**. Each project frames a real business question, works with realistic (synthetic)
data, and ends in **decisions a stakeholder can act on** — not just code.

> All datasets are synthetic and generated from seeded scripts, so every result is fully
> reproducible and no real/private data is involved.

---

## 🗂️ The projects

| # | Project | What it proves | Stack |
|---|---------|----------------|-------|
| 1 | **[Retail Sales SQL Analytics](01-retail-sales-sql/)** | Joins, CTEs, window functions, RFM segmentation, cohort retention | SQLite, SQL, Python |
| 2 | **[Customer Churn Analysis](02-customer-churn-analysis/)** | EDA, statistics, logistic regression, driver analysis, recommendations | pandas, scikit-learn, matplotlib |
| 3 | **[Sales KPI Dashboard](03-sales-kpi-dashboard/)** | Interactive BI: KPIs, trends, drill-downs, profitability analysis | Streamlit, pandas |
| 4 | **[A/B Test Analysis](04-ab-test-analysis/)** | Hypothesis testing, confidence intervals, power, ship/no-ship decision | scipy, statsmodels |
| 5 | **[Data Cleaning & ETL Pipeline](05-data-cleaning-etl/)** | Real-world data wrangling, validation, data-quality reporting | pandas |
| 6 | **[Excel Sales Dashboard](06-excel-sales-dashboard/)** | Formula-driven Excel: KPIs, `SUMIFS`, pivot-style tables, charts | openpyxl, Excel |

A common **retail/commerce thread** runs through the projects, so they read as one coherent
analyst story rather than unrelated demos.

---

## 🧰 Skills demonstrated

- **SQL:** multi-table joins, CTEs, `LAG`/`RANK`/`NTILE`, running totals, cohort & RFM analysis
- **Python:** pandas data wrangling, EDA, matplotlib visualisation
- **Statistics & experimentation:** A/B testing, two-proportion z-test, confidence intervals, statistical power
- **Machine learning:** logistic regression, train/test evaluation, ROC-AUC, odds-ratio interpretation
- **Data engineering basics:** documented ETL pipeline, data-quality validation gates, auditable cleaning
- **BI / dashboarding:** KPI design, interactive filtering, profitability analysis (Streamlit; transfers to Power BI / Tableau)
- **Excel:** formula-driven dashboards (`SUM`/`SUMIF`/`SUMIFS`), pivot-style summaries, native charts
- **Business communication:** every project ends in findings and recommendations

---

## ▶️ Quick start

Each project is independent with its own `README.md` and run instructions. In general:

```bash
# Project 1 — SQL analytics
cd 01-retail-sales-sql
python data/generate_data.py && python run_queries.py

# Project 2 — Churn analysis
cd 02-customer-churn-analysis
pip install -r requirements.txt
python data/generate_churn_data.py && python churn_analysis.py

# Project 3 — KPI dashboard
cd 03-sales-kpi-dashboard
pip install -r requirements.txt
python data/generate_sales.py && streamlit run app.py

# Project 4 — A/B test analysis
cd 04-ab-test-analysis
pip install -r requirements.txt
python data/generate_experiment.py && python ab_test_analysis.py

# Project 5 — Data cleaning & ETL
cd 05-data-cleaning-etl
python data/generate_messy_data.py && python etl_pipeline.py

# Project 6 — Excel dashboard
cd 06-excel-sales-dashboard
python build_dashboard.py        # then open Sales_Dashboard.xlsx
```

---

## 💬 How to talk about these in an interview

- **Project 1:** "I modelled an e-commerce business in SQL and answered growth, product-mix,
  customer-value (RFM) and retention (cohort) questions using window functions."
- **Project 2:** "I built a churn model that reaches 0.82 ROC-AUC, then translated the
  coefficients into odds ratios to tell the retention team *which* levers to pull — contract
  type and early-tenure onboarding were the biggest."
- **Project 3:** "I shipped a self-serve KPI dashboard that let stakeholders filter by region
  and segment, and it surfaced a loss-making product line and a discount threshold past which
  orders stop being profitable."
- **Project 4:** "I analysed a checkout A/B test end to end — SRM sanity check, two-proportion
  z-test with a confidence interval, a revenue guardrail metric and a power check — and made a
  defensible ship decision on a +14% conversion lift."
- **Project 5:** "I built an auditable ETL pipeline that takes a messy extract — mixed date
  formats, currency symbols, duplicates, impossible values — and cleans it to 97% completeness
  with validation gates that fail loudly if quality drops."
- **Project 6:** "I built a fully formula-driven Excel dashboard — KPIs and pivot-style tables
  on `SUMIFS`, with charts that recalc automatically when the source data changes."
