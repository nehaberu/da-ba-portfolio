"""
Generate a 'Superstore'-style sales dataset for the KPI dashboard.

One row per order line, with date, geography, category, sales, profit and
discount — the shape a BI/dashboard tool (Power BI, Tableau, Streamlit) consumes.

Run:  python data/generate_sales.py  ->  data/sales.csv
"""
import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(2024)
HERE = os.path.dirname(os.path.abspath(__file__))
N = 12_000
START = pd.Timestamp("2022-01-01")
END = pd.Timestamp("2024-12-31")

REGIONS = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
CATEGORIES = {
    "Technology": ["Phones", "Laptops", "Accessories", "Networking"],
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Labels"],
}
# baseline margin by category (Furniture is famously low-margin)
MARGIN = {"Technology": 0.16, "Furniture": 0.04, "Office Supplies": 0.13}


def main() -> None:
    days = (END - START).days
    # orders rise over time + a Q4 seasonal bump
    raw_offset = RNG.beta(2.2, 2.0, N) * days
    order_date = START + pd.to_timedelta(raw_offset.astype(int), unit="D")
    month = order_date.month

    category = RNG.choice(list(CATEGORIES), N, p=[0.36, 0.21, 0.43])
    sub_category = [RNG.choice(CATEGORIES[c]) for c in category]
    region = RNG.choice(REGIONS, N, p=[0.22, 0.20, 0.21, 0.24, 0.13])
    segment = RNG.choice(SEGMENTS, N, p=[0.52, 0.30, 0.18])

    base_price = {"Technology": 320, "Furniture": 240, "Office Supplies": 45}
    sales = np.array([RNG.gamma(2.0, base_price[c] / 2) for c in category])
    # Q4 (Nov/Dec) gets a lift
    sales *= np.where(np.isin(month, [11, 12]), RNG.uniform(1.1, 1.4, N), 1.0)
    sales = sales.round(2)

    discount = np.clip(RNG.choice([0, 0.1, 0.15, 0.2, 0.3], N,
                                  p=[0.45, 0.2, 0.15, 0.12, 0.08]), 0, 0.3)
    margin = np.array([MARGIN[c] for c in category])
    # discounts eat into profit; deep discounts can go negative
    profit = (sales * (margin - discount * 0.6) + RNG.normal(0, 8, N)).round(2)
    quantity = RNG.integers(1, 6, N)

    df = pd.DataFrame({
        "order_id": [f"ORD-{i:06d}" for i in range(1, N + 1)],
        "order_date": order_date.strftime("%Y-%m-%d"),
        "region": region,
        "segment": segment,
        "category": category,
        "sub_category": sub_category,
        "quantity": quantity,
        "discount": discount,
        "sales": sales,
        "profit": profit,
    }).sort_values("order_date").reset_index(drop=True)

    out = os.path.join(HERE, "sales.csv")
    df.to_csv(out, index=False)
    print(f"Wrote {out}")
    print(f"  rows: {len(df):,} | sales: {df.sales.sum():,.0f} | "
          f"profit: {df.profit.sum():,.0f} | margin: {df.profit.sum()/df.sales.sum():.1%}")


if __name__ == "__main__":
    main()
