# Sales KPI Dashboard (Streamlit)

An interactive **self-serve BI dashboard** over a Superstore-style sales dataset
(**12,000 order lines, 2022–2024**). Sidebar filters drive live KPI cards, trend lines
and breakdowns — the kind of tool a Business Analyst builds so stakeholders can answer
their own questions instead of waiting on ad-hoc reports.

---

##  Features

- **KPI cards** — Total Sales, Total Profit, Profit Margin, Avg Order Value, with a
  month-over-month delta.
- **Filters** — date range, region, segment and category; every chart updates live.
- **Trend** — monthly sales & profit line chart.
- **Breakdowns** — sales by category, profit by region.
- **Profitability watch-out** — margin by sub-category, highlighting loss-makers.
- **Discount impact** — average profit per order line at each discount tier.

---

## Project structure

```
03-sales-kpi-dashboard/
├── data/
│   ├── generate_sales.py   # builds the synthetic dataset (seeded)
│   └── sales.csv           # 12,000 order lines
├── app.py                  # the Streamlit dashboard
└── requirements.txt
```


##  Example insights the dashboard reveals

- **Technology drives the majority of sales** (~€1.46M of €2.36M) but **Furniture runs
  thin margins** — the *Tables* sub-category is actually **loss-making (−1.6%)**.
- **Discounting past ~20% turns the average order unprofitable** — a clear, defensible
  recommendation to cap discount authority.
- **Profit varies by region**, pointing to where commercial focus pays off.

---
