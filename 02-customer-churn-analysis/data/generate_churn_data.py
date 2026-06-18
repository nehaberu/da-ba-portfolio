"""
Generate a realistic synthetic telecom customer-churn dataset.

Churn is driven by a transparent latent model (short tenure, month-to-month
contracts, high monthly charges and lack of support services all increase the
probability of leaving) so that the downstream EDA and logistic-regression model
recover sensible, explainable drivers.

Run:  python data/generate_churn_data.py  ->  data/telco_churn.csv
"""
import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))
N = 7_000


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def main() -> None:
    contract = RNG.choice(
        ["Month-to-month", "One year", "Two year"], N, p=[0.55, 0.25, 0.20]
    )
    internet = RNG.choice(["DSL", "Fiber optic", "No"], N, p=[0.34, 0.46, 0.20])
    payment = RNG.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        N, p=[0.34, 0.23, 0.22, 0.21],
    )
    paperless = RNG.choice(["Yes", "No"], N, p=[0.59, 0.41])
    senior = RNG.choice([0, 1], N, p=[0.84, 0.16])
    partner = RNG.choice(["Yes", "No"], N, p=[0.48, 0.52])
    dependents = RNG.choice(["Yes", "No"], N, p=[0.30, 0.70])
    tech_support = RNG.choice(["Yes", "No"], N, p=[0.37, 0.63])
    online_security = RNG.choice(["Yes", "No"], N, p=[0.35, 0.65])

    # tenure correlates with contract length
    base_tenure = {"Month-to-month": 14, "One year": 34, "Two year": 50}
    tenure = np.clip(
        np.array([RNG.normal(base_tenure[c], 16) for c in contract]), 1, 72
    ).round().astype(int)

    # monthly charges depend on internet service
    base_charge = np.where(internet == "Fiber optic", 80,
                   np.where(internet == "DSL", 55, 25))
    monthly_charges = np.clip(base_charge + RNG.normal(0, 12, N), 18, 130).round(2)
    total_charges = (monthly_charges * tenure * RNG.uniform(0.9, 1.05, N)).round(2)

    # ---- latent churn model (interpretable coefficients) ----
    z = (
        -1.1
        + 1.30 * (contract == "Month-to-month")
        - 0.90 * (contract == "Two year")
        + 0.90 * (internet == "Fiber optic")     # fiber is pricier -> more churn
        - 0.030 * tenure                          # loyalty effect
        + 0.012 * (monthly_charges - 65)
        - 0.55 * (tech_support == "Yes")
        - 0.45 * (online_security == "Yes")
        + 0.40 * (payment == "Electronic check")
        + 0.30 * senior
        - 0.25 * (partner == "Yes")
        + RNG.normal(0, 0.45, N)                  # noise
    )
    churn_prob = sigmoid(z)
    churn = (RNG.uniform(0, 1, N) < churn_prob).astype(int)

    df = pd.DataFrame({
        "customer_id": [f"C{100000 + i}" for i in range(N)],
        "senior_citizen": senior,
        "partner": partner,
        "dependents": dependents,
        "tenure_months": tenure,
        "contract": contract,
        "internet_service": internet,
        "online_security": online_security,
        "tech_support": tech_support,
        "paperless_billing": paperless,
        "payment_method": payment,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "churn": np.where(churn == 1, "Yes", "No"),
    })

    out = os.path.join(HERE, "telco_churn.csv")
    df.to_csv(out, index=False)
    rate = (df["churn"] == "Yes").mean()
    print(f"Wrote {out}")
    print(f"  rows: {len(df):,} | churn rate: {rate:.1%}")


if __name__ == "__main__":
    main()
