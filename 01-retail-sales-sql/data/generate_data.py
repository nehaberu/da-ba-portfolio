"""
Generate a realistic synthetic e-commerce dataset and load it into a SQLite database.

Creates four related tables (customers, products, orders, order_items) modelled on a
typical online retailer, then writes them to `retail.db` in the project root.

Run:  python data/generate_data.py
"""
import os
import sqlite3
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)  # fixed seed -> reproducible dataset
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
DB_PATH = os.path.join(PROJECT_ROOT, "retail.db")

N_CUSTOMERS = 4_000
N_ORDERS = 18_000
START_DATE = pd.Timestamp("2023-01-01")
END_DATE = pd.Timestamp("2024-12-31")

COUNTRIES = ["Germany", "France", "UK", "Netherlands", "Spain", "Italy", "Poland", "Austria"]
COUNTRY_WEIGHTS = [0.34, 0.14, 0.13, 0.09, 0.09, 0.08, 0.07, 0.06]
CHANNELS = ["Organic", "Paid Search", "Social", "Email", "Referral"]
CHANNEL_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]

CATEGORIES = {
    "Electronics": (40, 900),
    "Home & Kitchen": (15, 250),
    "Apparel": (12, 120),
    "Beauty": (8, 80),
    "Sports": (20, 300),
    "Books": (6, 40),
}


def make_customers() -> pd.DataFrame:
    ids = np.arange(1, N_CUSTOMERS + 1)
    # signup spread across the window, weighted slightly toward earlier dates
    signup_offsets = RNG.beta(2, 3, N_CUSTOMERS) * (END_DATE - START_DATE).days
    signup = START_DATE + pd.to_timedelta(signup_offsets.astype(int), unit="D")
    return pd.DataFrame({
        "customer_id": ids,
        "signup_date": signup.strftime("%Y-%m-%d"),
        "country": RNG.choice(COUNTRIES, N_CUSTOMERS, p=COUNTRY_WEIGHTS),
        "acquisition_channel": RNG.choice(CHANNELS, N_CUSTOMERS, p=CHANNEL_WEIGHTS),
    })


def make_products() -> pd.DataFrame:
    rows = []
    pid = 1
    for category, (low, high) in CATEGORIES.items():
        n = RNG.integers(18, 30)
        for _ in range(n):
            price = round(float(RNG.uniform(low, high)), 2)
            rows.append({
                "product_id": pid,
                "product_name": f"{category[:4].upper()}-{pid:04d}",
                "category": category,
                "unit_price": price,
            })
            pid += 1
    return pd.DataFrame(rows)


def make_orders(customers: pd.DataFrame) -> pd.DataFrame:
    # repeat customers are more likely to be picked again -> realistic skew
    cust_weight = RNG.gamma(2.0, 1.0, len(customers))
    cust_weight /= cust_weight.sum()
    order_customers = RNG.choice(customers["customer_id"], N_ORDERS, p=cust_weight)

    signup_lookup = dict(zip(customers["customer_id"], pd.to_datetime(customers["signup_date"])))
    order_dates, statuses = [], []
    for cid in order_customers:
        signup = signup_lookup[cid]
        max_days = (END_DATE - signup).days
        offset = int(RNG.uniform(0, max(max_days, 1)))
        d = signup + pd.Timedelta(days=offset)
        # mild seasonal lift in Nov/Dec
        order_dates.append(d)
    statuses = RNG.choice(["completed", "returned", "cancelled"], N_ORDERS, p=[0.88, 0.08, 0.04])

    return pd.DataFrame({
        "order_id": np.arange(1, N_ORDERS + 1),
        "customer_id": order_customers,
        "order_date": pd.to_datetime(order_dates).strftime("%Y-%m-%d"),
        "channel": RNG.choice(CHANNELS, N_ORDERS, p=CHANNEL_WEIGHTS),
        "status": statuses,
    })


def make_order_items(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    rows = []
    item_id = 1
    prod_ids = products["product_id"].to_numpy()
    price_lookup = dict(zip(products["product_id"], products["unit_price"]))
    for oid in orders["order_id"]:
        n_lines = int(RNG.choice([1, 2, 3, 4], p=[0.55, 0.27, 0.12, 0.06]))
        chosen = RNG.choice(prod_ids, n_lines, replace=False)
        for pid in chosen:
            qty = int(RNG.choice([1, 2, 3], p=[0.75, 0.18, 0.07]))
            rows.append({
                "order_item_id": item_id,
                "order_id": int(oid),
                "product_id": int(pid),
                "quantity": qty,
                "unit_price": price_lookup[pid],
            })
            item_id += 1
    return pd.DataFrame(rows)


def main() -> None:
    print("Generating customers, products, orders, order_items ...")
    customers = make_customers()
    products = make_products()
    orders = make_orders(customers)
    order_items = make_order_items(orders, products)

    # also drop CSV copies so the data is browsable on GitHub without opening the .db
    for name, df in [("customers", customers), ("products", products),
                     ("orders", orders), ("order_items", order_items)]:
        df.to_csv(os.path.join(HERE, f"{name}.csv"), index=False)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    customers.to_sql("customers", conn, index=False)
    products.to_sql("products", conn, index=False)
    orders.to_sql("orders", conn, index=False)
    order_items.to_sql("order_items", conn, index=False)
    conn.commit()
    conn.close()

    print(f"Done. Wrote {DB_PATH}")
    print(f"  customers   : {len(customers):>6,}")
    print(f"  products    : {len(products):>6,}")
    print(f"  orders      : {len(orders):>6,}")
    print(f"  order_items : {len(order_items):>6,}")


if __name__ == "__main__":
    main()
