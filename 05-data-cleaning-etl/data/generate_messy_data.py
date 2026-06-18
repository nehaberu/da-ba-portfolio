"""
Generate a deliberately MESSY raw sales/CRM extract.

Real-world data is rarely clean. This script injects the dirt an analyst actually
meets, so the ETL pipeline has something real to fix:
  - inconsistent date formats          (2024-03-05, 05/03/2024, March 5 2024, ...)
  - messy categorical values           ("  germany", "DE", "Deutschland", "Germany ")
  - currency symbols & thousands separators in numeric columns ("€1,299.00")
  - missing values (blank, "N/A", "null", "-")
  - duplicate rows
  - leading/trailing whitespace and inconsistent casing in emails/names
  - impossible / out-of-range values    (negative quantity, age 250)

Run:  python data/generate_messy_data.py  ->  data/raw_sales.csv
"""
import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(55)
HERE = os.path.dirname(os.path.abspath(__file__))
N = 2_500

COUNTRY_VARIANTS = {
    "Germany": ["Germany", " germany", "DE", "Deutschland", "GERMANY ", "germany"],
    "France": ["France", "FR", "france ", " France"],
    "UK": ["UK", "United Kingdom", "U.K.", "uk", "England"],
    "Netherlands": ["Netherlands", "NL", "netherlands", "The Netherlands"],
    "Spain": ["Spain", "ES", "spain ", "España"],
}
CATEGORIES = ["Electronics", "Furniture", "Office Supplies"]
FIRST = ["Anna", "Lukas", "Marie", "Jonas", "Sofia", "Felix", "Emma", "Paul"]
LAST = ["Müller", "Schmidt", "Weber", "Fischer", "Becker", "Wagner", "Klein"]


def messy_date(d: pd.Timestamp) -> str:
    fmt = RNG.choice(["iso", "eu", "us_slash", "long", "dotted"])
    if fmt == "iso":
        return d.strftime("%Y-%m-%d")
    if fmt == "eu":
        return d.strftime("%d/%m/%Y")
    if fmt == "us_slash":
        return d.strftime("%m/%d/%Y")
    if fmt == "dotted":
        return d.strftime("%d.%m.%Y")
    return d.strftime("%B %d %Y")


def messy_money(x: float) -> str:
    style = RNG.choice(["plain", "euro", "comma", "euro_comma"])
    if style == "plain":
        return f"{x:.2f}"
    if style == "euro":
        return f"€{x:.2f}"
    if style == "comma":
        return f"{x:,.2f}"
    return f"€{x:,.2f}"


def maybe_missing(val, p=0.06):
    if RNG.uniform() < p:
        return RNG.choice(["", "N/A", "null", "-", " "])
    return val


def main() -> None:
    rows = []
    base = pd.Timestamp("2024-01-01")
    for i in range(N):
        canon_country = RNG.choice(list(COUNTRY_VARIANTS))
        country = RNG.choice(COUNTRY_VARIANTS[canon_country])
        d = base + pd.Timedelta(days=int(RNG.integers(0, 270)))
        qty = int(RNG.integers(1, 6))
        # inject a few impossible values
        if RNG.uniform() < 0.02:
            qty = -qty
        price = float(RNG.uniform(15, 1500))
        age = int(RNG.integers(18, 70))
        if RNG.uniform() < 0.015:
            age = int(RNG.integers(150, 260))  # impossible age
        fname, lname = RNG.choice(FIRST), RNG.choice(LAST)
        email_case = RNG.choice([str.lower, str.upper, str.title])
        email = email_case(f"  {fname}.{lname}@example.com  ")

        rows.append({
            "order_id": f"ORD{1000 + i}",
            "order_date": messy_date(d),
            "customer_name": RNG.choice([f"  {fname} {lname}", f"{fname}  {lname} ",
                                         f"{fname} {lname}"]),
            "email": maybe_missing(email),
            "country": country,
            "category": maybe_missing(RNG.choice(CATEGORIES), p=0.04),
            "quantity": maybe_missing(qty, p=0.03),
            "unit_price": maybe_missing(messy_money(price), p=0.05),
            "customer_age": maybe_missing(age, p=0.05),
        })

    df = pd.DataFrame(rows)
    # add ~3% exact duplicate rows
    dups = df.sample(frac=0.03, random_state=1)
    df = pd.concat([df, dups], ignore_index=True)
    df = df.sample(frac=1.0, random_state=2).reset_index(drop=True)  # shuffle

    out = os.path.join(HERE, "raw_sales.csv")
    df.to_csv(out, index=False)
    print(f"Wrote {out}  ({len(df):,} rows, intentionally messy)")
    print(df.head(6).to_string(index=False))


if __name__ == "__main__":
    main()
