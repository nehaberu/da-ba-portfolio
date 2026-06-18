# 📊 Sales KPI Dashboard (Streamlit)

An interactive **self-serve BI dashboard** over a Superstore-style sales dataset
(**12,000 order lines, 2022–2024**). Sidebar filters drive live KPI cards, trend lines
and breakdowns — the kind of tool a Business Analyst builds so stakeholders can answer
their own questions instead of waiting on ad-hoc reports.

> **Why this project matters in an interview:** it proves you can do the BI/dashboarding
> part of the job (KPIs, trends, drill-downs, interactivity) in code that anyone can run —
> the same thinking transfers directly to **Power BI / Tableau / Looker**. It also shows
> commercial instinct: the dashboard surfaces **loss-making sub-categories** and the point
> where **discounting destroys profit**.

---

## ✨ Features

- **KPI cards** — Total Sales, Total Profit, Profit Margin, Avg Order Value, with a
  month-over-month delta.
- **Filters** — date range, region, segment and category; every chart updates live.
- **Trend** — monthly sales & profit line chart.
- **Breakdowns** — sales by category, profit by region.
- **Profitability watch-out** — margin by sub-category, highlighting loss-makers.
- **Discount impact** — average profit per order line at each discount tier.

---

## 📁 Project structure

```
03-sales-kpi-dashboard/
├── data/
│   ├── generate_sales.py   # builds the synthetic dataset (seeded)
│   └── sales.csv           # 12,000 order lines
├── app.py                  # the Streamlit dashboard
└── requirements.txt
```

## ▶️ How to run

```bash
pip install -r requirements.txt
python data/generate_sales.py     # creates data/sales.csv
streamlit run app.py              # opens at http://localhost:8501
```

> 💡 **Free hosting:** push to GitHub and deploy in two clicks on
> [Streamlit Community Cloud](https://streamlit.io/cloud) — then your CV can link to a
> **live** dashboard, which stands out to recruiters.

---

## 📊 Example insights the dashboard reveals

- **Technology drives the majority of sales** (~€1.46M of €2.36M) but **Furniture runs
  thin margins** — the *Tables* sub-category is actually **loss-making (−1.6%)**.
- **Discounting past ~20% turns the average order unprofitable** — a clear, defensible
  recommendation to cap discount authority.
- **Profit varies by region**, pointing to where commercial focus pays off.

*Dataset is fully synthetic and generated with a fixed random seed — no real data.*

---

### 📸 Add a screenshot

Run the app, take a screenshot of the dashboard, save it as `screenshot.png` in this
folder, then add it here so recruiters see it without running anything:

```markdown
![Dashboard](screenshot.png)
```
