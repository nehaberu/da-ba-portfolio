# 📈 Data & Business Analyst Portfolio

Three self-contained, interview-ready projects covering the skills that show up in almost
every **Data Analyst / Business Analyst** job description: **SQL**, **Python analytics &
machine learning**, and **BI dashboarding**. Each project frames a real business question,
works with realistic (synthetic) data, and ends in **decisions a stakeholder can act on** —
not just code.

> All datasets are synthetic and generated from seeded scripts, so every result is fully
> reproducible and no real/private data is involved.

---

## 🗂️ The projects

| # | Project | What it proves | Stack |
|---|---------|----------------|-------|
| 1 | **[Retail Sales SQL Analytics](01-retail-sales-sql/)** | Joins, CTEs, window functions, RFM segmentation, cohort retention | SQLite, SQL, Python |
| 2 | **[Customer Churn Analysis](02-customer-churn-analysis/)** | EDA, statistics, logistic regression, driver analysis, recommendations | pandas, scikit-learn, matplotlib |
| 3 | **[Sales KPI Dashboard](03-sales-kpi-dashboard/)** | Interactive BI: KPIs, trends, drill-downs, profitability analysis | Streamlit, pandas |

A common **retail thread** runs through all three, so they read as one coherent analyst
story rather than three unrelated demos.

---

## 🧰 Skills demonstrated

- **SQL:** multi-table joins, CTEs, `LAG`/`RANK`/`NTILE`, running totals, cohort & RFM analysis
- **Python:** pandas data wrangling, EDA, matplotlib visualisation
- **Statistics & ML:** logistic regression, train/test evaluation, ROC-AUC, odds-ratio interpretation
- **BI / dashboarding:** KPI design, interactive filtering, profitability & discount analysis (Streamlit; transfers to Power BI / Tableau)
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
