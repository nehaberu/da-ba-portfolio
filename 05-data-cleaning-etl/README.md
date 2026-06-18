# 🧹 Data Cleaning & ETL Pipeline

A documented, auditable pipeline that turns a **messy raw sales/CRM extract** into a
**clean, analytics-ready table** — the unglamorous data-wrangling work that is ~80% of a
real Data/Business Analyst's job (and the part portfolios usually skip).

> **Why this project matters in an interview:** anyone can run a chart on clean data. This
> shows you can handle *dirty* data the way it actually arrives — mixed date formats,
> currency symbols, inconsistent country spellings, missing-value tokens, duplicates and
> impossible values — with a repeatable, **logged and validated** process you can defend.

---

## 🗃️ The mess (intentionally injected into the raw file)

| Problem | Example |
|---------|---------|
| Inconsistent date formats | `2024-01-16`, `04/01/2024`, `March 23 2024`, `07.04.2024` |
| Country spelling variants | `germany`, `DE`, `Deutschland`, `GERMANY ` → **Germany** |
| Currency symbols & separators | `€1,041.54` → `1041.54` |
| Missing-value tokens | `""`, `N/A`, `null`, `-` → real `NaN` |
| Duplicate rows | ~3% exact duplicates |
| Whitespace / casing | `  Paul  Becker `, `SOFIA.WAGNER@EXAMPLE.COM` |
| Impossible values | negative quantity, age 250 |

---

## 📁 Project structure

```
05-data-cleaning-etl/
├── data/
│   ├── generate_messy_data.py   # creates the dirty raw extract (seeded)
│   ├── raw_sales.csv            # messy input  (~2,575 rows)
│   └── clean_sales.csv          # cleaned output (written by the pipeline)
├── etl_pipeline.py              # EXTRACT → PROFILE → TRANSFORM → VALIDATE → LOAD
├── data_quality_report.txt      # before/after report (written by the pipeline)
└── (README.md)
```

## ▶️ How to run

```bash
pip install pandas numpy
python data/generate_messy_data.py   # creates the messy raw file
python etl_pipeline.py               # cleans it + writes the report
```

---

## ⚙️ Pipeline design

The pipeline follows a clear **EXTRACT → PROFILE → TRANSFORM → VALIDATE → LOAD** structure,
and **every transform logs how many values it changed**, so the cleaning is fully auditable:

1. Drop exact duplicate rows
2. Standardise `country` to 5 canonical values via a mapping
3. Parse mixed date formats into a single ISO datetime
4. Strip currency symbols/separators → numeric `unit_price`
5. Coerce numerics and enforce **range rules** (no negative quantities, ages 18–100)
6. Trim whitespace, title-case names, lower-case emails, flag invalid email formats
7. Derive `revenue` and impute missing prices with the **category median**

Then **quality gates** assert the result is clean (no dupes, canonical countries, valid
ranges, dates parsed) — the pipeline *fails loudly* if any gate breaks.

---

## 📊 Result (typical run)

```
rows in : 2,575   ->   rows out : 2,500   (75 duplicates removed)
57 non-positive quantities nulled · 34 impossible ages nulled
132 missing prices imputed (category median)
overall completeness: 96.9%
ALL quality gates: PASS
```

The full before/after breakdown is saved to **`data_quality_report.txt`** on every run, so
the cleaning is reproducible and reviewable.

*Both the messy input and the cleaning logic are synthetic and seeded — fully reproducible.*
