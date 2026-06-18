"""
Generate a realistic A/B test dataset for an e-commerce checkout experiment.

Scenario
--------
An online store tests a new one-page checkout (treatment) against the current
multi-step checkout (control). Each row is one user session randomly assigned to
a group, with whether they converted (placed an order) and how much they spent.

The treatment has a genuine but modest lift in conversion, so the downstream
statistical tests should detect a significant — but not enormous — effect.

Run:  python data/generate_experiment.py  ->  data/experiment.csv
"""
import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(101)
HERE = os.path.dirname(os.path.abspath(__file__))
N = 40_000

# true (hidden) parameters we will try to recover with statistics
CONTROL_CONV = 0.110          # baseline conversion rate
TREATMENT_CONV = 0.124        # ~1.4pp absolute lift (~12.7% relative)
AOV_CONTROL = 58.0            # average order value among converters
AOV_TREATMENT = 59.5          # slightly higher basket too


def main() -> None:
    group = RNG.choice(["control", "treatment"], N, p=[0.5, 0.5])
    device = RNG.choice(["mobile", "desktop", "tablet"], N, p=[0.62, 0.32, 0.06])

    conv_p = np.where(group == "treatment", TREATMENT_CONV, CONTROL_CONV)
    converted = (RNG.uniform(0, 1, N) < conv_p).astype(int)

    # revenue is 0 for non-converters, gamma-distributed for converters
    aov = np.where(group == "treatment", AOV_TREATMENT, AOV_CONTROL)
    revenue = np.where(
        converted == 1,
        RNG.gamma(shape=4.0, scale=aov / 4.0, size=N),
        0.0,
    ).round(2)

    # spread the experiment over a 3-week run
    day = RNG.integers(1, 22, N)
    date = pd.Timestamp("2024-09-01") + pd.to_timedelta(day - 1, unit="D")

    df = pd.DataFrame({
        "user_id": [f"U{200000 + i}" for i in range(N)],
        "date": date.strftime("%Y-%m-%d"),
        "group": group,
        "device": device,
        "converted": converted,
        "revenue": revenue,
    })

    out = os.path.join(HERE, "experiment.csv")
    df.to_csv(out, index=False)
    print(f"Wrote {out}")
    for g in ["control", "treatment"]:
        sub = df[df.group == g]
        print(f"  {g:9s}: n={len(sub):,}  conv={sub.converted.mean():.3%}  "
              f"rev/user=€{sub.revenue.mean():.2f}")


if __name__ == "__main__":
    main()
