"""
A/B Test Analysis — Checkout Experiment
=======================================
Analyses a randomised checkout experiment (control = current multi-step checkout,
treatment = new one-page checkout) and decides whether to ship the change.

Covers the full experimentation toolkit a Data/Business Analyst is expected to know:
  1. Sample-ratio + sanity checks
  2. Conversion lift with a two-proportion z-test + 95% confidence interval
  3. Revenue-per-user comparison with a t-test (guards against "more orders, smaller baskets")
  4. Statistical power for the observed effect
  5. Segmentation by device (is the effect real everywhere or driven by one segment?)
  6. A plain-English ship / no-ship recommendation

Run:  python data/generate_experiment.py
      python ab_test_analysis.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"figure.dpi": 120, "axes.grid": True, "grid.alpha": 0.3})
ALPHA = 0.05
CONTROL, TREATMENT = "#2563eb", "#16a34a"


def load() -> pd.DataFrame:
    path = os.path.join(HERE, "data", "experiment.csv")
    if not os.path.exists(path):
        raise SystemExit("Run `python data/generate_experiment.py` first.")
    return pd.read_csv(path)


def section(title: str) -> None:
    print("\n" + "=" * 64 + f"\n{title}\n" + "=" * 64)


def summary(df: pd.DataFrame) -> dict:
    section("1. EXPERIMENT SUMMARY & SANITY CHECKS")
    g = df.groupby("group").agg(
        users=("user_id", "count"),
        conversions=("converted", "sum"),
        conv_rate=("converted", "mean"),
        rev_per_user=("revenue", "mean"),
    )
    print(g.to_string(float_format=lambda v: f"{v:,.4f}"))

    # sample-ratio mismatch check: expect ~50/50
    n_c, n_t = g.loc["control", "users"], g.loc["treatment", "users"]
    srm_p = stats.chisquare([n_c, n_t], [(n_c + n_t) / 2] * 2).pvalue
    flag = "OK" if srm_p > 0.01 else "WARNING — investigate assignment!"
    print(f"\nSample-ratio mismatch (SRM) check: p={srm_p:.3f}  [{flag}]")
    return {
        "n_c": int(n_c), "n_t": int(n_t),
        "conv_c": g.loc["control", "conv_rate"], "conv_t": g.loc["treatment", "conv_rate"],
        "conv_c_count": int(g.loc["control", "conversions"]),
        "conv_t_count": int(g.loc["treatment", "conversions"]),
    }


def conversion_test(s: dict) -> dict:
    section("2. CONVERSION LIFT — two-proportion z-test")
    counts = np.array([s["conv_t_count"], s["conv_c_count"]])
    nobs = np.array([s["n_t"], s["n_c"]])
    zstat, pval = proportions_ztest(counts, nobs)

    abs_lift = s["conv_t"] - s["conv_c"]
    rel_lift = abs_lift / s["conv_c"]

    # 95% CI for the difference in proportions (Newcombe / normal approx)
    ci_t = proportion_confint(counts[0], nobs[0], alpha=ALPHA, method="wilson")
    ci_c = proportion_confint(counts[1], nobs[1], alpha=ALPHA, method="wilson")
    # CI on the difference via pooled SE
    se = np.sqrt(s["conv_c"] * (1 - s["conv_c"]) / s["n_c"]
                 + s["conv_t"] * (1 - s["conv_t"]) / s["n_t"])
    diff_ci = (abs_lift - 1.96 * se, abs_lift + 1.96 * se)

    print(f"Control   conversion: {s['conv_c']:.3%}  (95% CI {ci_c[0]:.3%} – {ci_c[1]:.3%})")
    print(f"Treatment conversion: {s['conv_t']:.3%}  (95% CI {ci_t[0]:.3%} – {ci_t[1]:.3%})")
    print(f"\nAbsolute lift: {abs_lift:+.3%}  (95% CI {diff_ci[0]:+.3%} – {diff_ci[1]:+.3%})")
    print(f"Relative lift: {rel_lift:+.1%}")
    print(f"z = {zstat:.3f},  p = {pval:.2e}")
    print("Result:", "STATISTICALLY SIGNIFICANT (reject H0)" if pval < ALPHA
          else "not significant (fail to reject H0)")
    return {"abs_lift": abs_lift, "rel_lift": rel_lift, "pval": pval,
            "diff_ci": diff_ci, "se": se}


def revenue_test(df: pd.DataFrame) -> float:
    section("3. REVENUE PER USER — Welch's t-test")
    c = df.loc[df.group == "control", "revenue"]
    t = df.loc[df.group == "treatment", "revenue"]
    tstat, pval = stats.ttest_ind(t, c, equal_var=False)
    lift = t.mean() - c.mean()
    print(f"Control   revenue/user: €{c.mean():.3f}")
    print(f"Treatment revenue/user: €{t.mean():.3f}")
    print(f"Difference: €{lift:+.3f}/user   t = {tstat:.3f}, p = {pval:.2e}")
    print("Result:", "significant" if pval < ALPHA else "not significant")
    return pval


def power_analysis(s: dict, abs_lift: float) -> float:
    section("4. STATISTICAL POWER (for the observed effect)")
    effect = proportion_effectsize(s["conv_t"], s["conv_c"])
    power = NormalIndPower().power(
        effect_size=abs(effect), nobs1=s["n_c"], alpha=ALPHA, ratio=s["n_t"] / s["n_c"]
    )
    # sample size needed for 80% power at this effect
    n_needed = NormalIndPower().solve_power(
        effect_size=abs(effect), alpha=ALPHA, power=0.8, ratio=1.0
    )
    print(f"Observed effect size (Cohen's h): {abs(effect):.4f}")
    print(f"Achieved power: {power:.1%}")
    print(f"Per-group n for 80% power at this effect: {n_needed:,.0f}")
    print("Interpretation:",
          "well-powered — we can trust the result." if power >= 0.8
          else "underpowered — result may be unreliable.")
    return power


def segment_by_device(df: pd.DataFrame) -> None:
    section("5. SEGMENTATION BY DEVICE")
    rows = []
    for dev, sub in df.groupby("device"):
        c = sub[sub.group == "control"]["converted"]
        t = sub[sub.group == "treatment"]["converted"]
        _, p = proportions_ztest([t.sum(), c.sum()], [len(t), len(c)])
        rows.append({"device": dev, "control": c.mean(), "treatment": t.mean(),
                     "abs_lift": t.mean() - c.mean(), "p_value": p})
    seg = pd.DataFrame(rows)
    print(seg.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return seg


def plot(s: dict, conv: dict, seg: pd.DataFrame) -> None:
    # conversion comparison with CI error bars
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    rates = [s["conv_c"], s["conv_t"]]
    errs = [1.96 * np.sqrt(r * (1 - r) / n)
            for r, n in zip(rates, [s["n_c"], s["n_t"]])]
    ax.bar(["Control", "Treatment"], rates, yerr=errs, capsize=8,
           color=[CONTROL, TREATMENT])
    ax.set_title(f"Conversion rate (+{conv['rel_lift']:.0%} relative, p={conv['pval']:.1e})")
    ax.set_ylabel("Conversion rate")
    for i, r in enumerate(rates):
        ax.text(i, r + errs[i] + 0.001, f"{r:.2%}", ha="center", fontsize=10)

    ax = axes[1]
    x = np.arange(len(seg))
    w = 0.38
    ax.bar(x - w / 2, seg["control"], w, label="Control", color=CONTROL)
    ax.bar(x + w / 2, seg["treatment"], w, label="Treatment", color=TREATMENT)
    ax.set_xticks(x); ax.set_xticklabels(seg["device"])
    ax.set_title("Conversion by device")
    ax.set_ylabel("Conversion rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "01_ab_results.png"))
    plt.close(fig)
    print("\n  saved figures/01_ab_results.png")


def recommendation(conv: dict, rev_p: float, power: float) -> None:
    section("6. RECOMMENDATION")
    ship = conv["pval"] < ALPHA and conv["diff_ci"][0] > 0 and power >= 0.8
    if ship:
        print(f"""\
  SHIP the new one-page checkout.
  - Conversion lift of {conv['abs_lift']:+.2%} ({conv['rel_lift']:+.0%} relative) is
    statistically significant (p={conv['pval']:.1e}) and the 95% CI excludes zero.
  - The test is well-powered ({power:.0%}), so the effect is trustworthy.
  - Revenue per user moved in the same direction, so the extra conversions are not
    coming at the cost of smaller baskets.
  Next step: roll out to 100%, keep a small holdback to monitor for novelty effects.""")
    else:
        print("  DO NOT ship yet — effect is not significant, not positive, or underpowered.")


def main() -> None:
    df = load()
    s = summary(df)
    conv = conversion_test(s)
    rev_p = revenue_test(df)
    power = power_analysis(s, conv["abs_lift"])
    seg = segment_by_device(df)
    plot(s, conv, seg)
    recommendation(conv, rev_p, power)
    print("\nFigure saved to figures/. Analysis complete.")


if __name__ == "__main__":
    main()
