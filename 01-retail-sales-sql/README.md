# 🛒 Retail Sales SQL Analytics

End-to-end **SQL analysis** of a synthetic European e-commerce retailer (~4,000 customers,
18,000 orders, 30,000 order lines across 2023–2024). The project answers the questions a
business stakeholder actually asks — *Is revenue growing? What sells? Who are our best
customers? Are we keeping them?* — using nothing but SQL.

> **Why this project matters in an interview:** it demonstrates the full SQL toolkit that
> Data/Business Analyst roles screen for — multi-table `JOIN`s, `CTE`s, window functions
> (`LAG`, `RANK`, `NTILE`, running totals), date arithmetic, and two textbook analytics
> patterns (**RFM segmentation** and **cohort retention**).

---

## 📁 Project structure

```
01-retail-sales-sql/
├── data/
│   ├── generate_data.py      # builds the synthetic dataset (seeded, reproducible)
│   ├── customers.csv         # generated copies, browsable on GitHub
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
├── queries/
│   ├── 01_schema_and_kpis.sql
│   ├── 02_monthly_revenue_growth.sql
│   ├── 03_top_products_and_categories.sql
│   ├── 04_rfm_segmentation.sql
│   └── 05_cohort_retention.sql
├── run_queries.py            # runs every query and prints the results
└── retail.db                 # SQLite database (created by generate_data.py)
```

## 🗄️ Data model

```
customers ──< orders ──< order_items >── products
```

| Table | Grain | Key columns |
|-------|-------|-------------|
| `customers`   | one row per customer | `customer_id`, `signup_date`, `country`, `acquisition_channel` |
| `products`    | one row per product  | `product_id`, `category`, `unit_price` |
| `orders`      | one row per order    | `order_id`, `customer_id`, `order_date`, `status` |
| `order_items` | one row per line     | `order_id`, `product_id`, `quantity`, `unit_price` |

**Revenue convention:** only `status = 'completed'` orders count; line revenue = `quantity × unit_price`.

---

## ▶️ How to run

```bash
pip install pandas numpy            # only needed to (re)generate data + pretty-print
python data/generate_data.py        # builds retail.db
python run_queries.py               # runs all 5 query files
python run_queries.py 04            # run just the RFM query

# ...or open retail.db in any SQL client / DB Browser for SQLite and run the .sql files
```

---

## 📊 Key findings

- **Strong, steady growth.** Monthly revenue climbed from a near-zero launch to **€460k by
  Dec 2024**, with total revenue of **€5.6M** across the period and an **average order value of €355**.
- **Revenue is highly concentrated.** Electronics alone drives **57%** of revenue; the top two
  categories account for **70%** — a classic Pareto distribution that tells the merchandising
  team where to focus.
- **A small group of "Champions" carries the business.** RFM segmentation surfaces high-value,
  highly-engaged customers (e.g. 27 orders / €13k lifetime) alongside an **"At Risk (high value)"**
  segment — customers who used to spend heavily but have gone quiet and are worth a win-back campaign.
- **Retention stabilises around 20–30%.** Cohort analysis shows new customers settle into a
  repeat-purchase rate of roughly a quarter after the first month — a realistic e-commerce curve
  and a baseline to improve against.

---

## 🧠 SQL techniques demonstrated

| Technique | Where |
|-----------|-------|
| Multi-table `JOIN` + filtered aggregation | every query |
| `CTE` chaining for readable pipelines | 02, 03, 04, 05 |
| `LAG()` for Month-over-Month growth | 02 |
| `RANK()` + running total / share-of-total | 03 |
| `NTILE()` quintile scoring + `CASE` segmentation | 04 (RFM) |
| First-touch cohort + month-offset retention | 05 |

*Dataset is fully synthetic and generated with a fixed random seed — no real customer data.*
