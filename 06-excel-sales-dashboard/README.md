# 📊 Excel Sales Dashboard

A **formula-driven Excel dashboard** built programmatically from a clean transactional
sales table. Excel appears in almost every Data/Business Analyst job description — this
project shows the skill done *properly*: KPIs, summary tables and charts powered by **live
Excel formulas**, not numbers pasted in from somewhere else.

> **Why this project matters in an interview:** it proves you understand how Excel is used
> on the job — a single source-of-truth data sheet, and a dashboard of **`SUM` / `SUMIF` /
> `SUMIFS`** formulas plus native charts that **recalculate automatically** when the data
> changes. The same modelling logic transfers straight to Power BI / Tableau measures.

---

## 📁 What's in the workbook

`Sales_Dashboard.xlsx` has two sheets:

| Sheet | Contents |
|-------|----------|
| **Data** | 1,500 sales transactions — Order ID, Date, Region, Segment, Category, Quantity, Sales, Profit. Frozen header row + auto-filter. The single source of truth. |
| **Dashboard** | 5 KPI cards, 3 summary tables and 3 charts — **all live formulas** referencing the Data sheet. |

**KPI cards:** Total Sales, Total Profit, Profit Margin, Total Orders, Avg Order Value.

**Summary tables (formula-driven):**
- Monthly Sales — `SUMIFS` over a month date-window
- Sales by Category — `SUMIF`
- Profit by Region — `SUMIF`

**Charts:** monthly sales trend (line), sales by category (bar), profit by region (bar).

---

## 🔑 The key idea: it's dynamic

Every dashboard number is an Excel formula, e.g.

```
Total Sales      =SUM(Data!$G$2:$G$1501)
Profit Margin    =C4/B4
Monthly Sales    =SUMIFS(Data!$G$2:$G$1501, Data!$B$2:$B$1501, ">="&DATE(2024,1,1),
                                            Data!$B$2:$B$1501, "<"&DATE(2024,2,1))
Sales by Category=SUMIF(Data!$E$2:$E$1501, E8, Data!$G$2:$G$1501)
```

Change any value on the **Data** sheet and the KPIs, tables and charts update by themselves.

---

## ▶️ How to (re)build it

```bash
pip install openpyxl pandas numpy
python build_dashboard.py        # regenerates Sales_Dashboard.xlsx
```

The script also prints a verification of the totals (Excel formulas vs a pandas
ground-truth calculation) so you can confirm the numbers are right.

> **Note:** the file is saved with *full recalculation on load*, so just **open it in Excel,
> Numbers or Google Sheets** and all formulas/charts populate instantly. To show it on
> GitHub, open the file and save a screenshot as `screenshot.png`, then add it here:
> `![Dashboard](screenshot.png)`.

---

## 📊 Example figures (this build)

| KPI | Value |
|-----|------:|
| Total Sales | €320,798 |
| Total Profit | €29,485 |
| Profit Margin | 9.2% |
| Total Orders | 1,500 |
| Avg Order Value | €214 |

Technology drives the majority of revenue (~€191k), while Furniture's thin margin keeps
overall profitability modest — the kind of insight the dashboard makes obvious at a glance.

*Data is synthetic and seeded — fully reproducible.*
