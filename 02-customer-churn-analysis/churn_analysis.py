"""
Customer Churn Analysis
=======================
End-to-end analysis of a telecom churn dataset:
  1. Load & quick data-quality check
  2. Exploratory data analysis (EDA) with saved charts
  3. Logistic-regression model to predict churn
  4. Driver analysis (which factors push customers to leave) + business recommendations

Outputs charts to figures/ and prints a written summary to the console.

Run:  python data/generate_churn_data.py   # build the dataset first
      python churn_analysis.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless: save PNGs without a display
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"figure.dpi": 120, "axes.grid": True, "grid.alpha": 0.3})
ACCENT = "#2563eb"
DANGER = "#dc2626"


def load_data() -> pd.DataFrame:
    path = os.path.join(HERE, "data", "telco_churn.csv")
    if not os.path.exists(path):
        raise SystemExit("Dataset missing. Run `python data/generate_churn_data.py` first.")
    df = pd.read_csv(path)
    df["churn_flag"] = (df["churn"] == "Yes").astype(int)
    return df


# ----------------------------------------------------------------------
# 1. Data quality
# ----------------------------------------------------------------------
def data_quality(df: pd.DataFrame) -> None:
    print("=" * 64)
    print("1. DATA QUALITY")
    print("=" * 64)
    print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")
    print(f"Missing values: {int(df.isna().sum().sum())}")
    print(f"Duplicate customer_ids: {df['customer_id'].duplicated().sum()}")
    print(f"Overall churn rate: {df['churn_flag'].mean():.1%}\n")


# ----------------------------------------------------------------------
# 2. EDA
# ----------------------------------------------------------------------
def churn_rate_by(df: pd.DataFrame, col: str) -> pd.Series:
    return df.groupby(col)["churn_flag"].mean().sort_values(ascending=False)


def plot_eda(df: pd.DataFrame) -> None:
    print("=" * 64)
    print("2. EXPLORATORY DATA ANALYSIS")
    print("=" * 64)

    # 2a. Churn rate by contract type
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, col, title in [
        (axes[0], "contract", "Churn rate by contract"),
        (axes[1], "internet_service", "Churn rate by internet service"),
    ]:
        s = churn_rate_by(df, col)
        ax.bar(s.index.astype(str), s.values, color=ACCENT)
        ax.set_title(title)
        ax.set_ylabel("Churn rate")
        for i, v in enumerate(s.values):
            ax.text(i, v + 0.01, f"{v:.0%}", ha="center", fontsize=9)
        ax.set_ylim(0, max(s.values) * 1.2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "01_churn_by_category.png"))
    plt.close(fig)
    print("  saved figures/01_churn_by_category.png")
    for col in ["contract", "internet_service", "payment_method"]:
        print(f"\n  Churn rate by {col}:")
        print(churn_rate_by(df, col).apply(lambda v: f"{v:.1%}").to_string())

    # 2b. Tenure distribution: churned vs retained
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df.loc[df.churn_flag == 0, "tenure_months"], bins=24, alpha=0.7,
            label="Retained", color=ACCENT)
    ax.hist(df.loc[df.churn_flag == 1, "tenure_months"], bins=24, alpha=0.7,
            label="Churned", color=DANGER)
    ax.set_title("Tenure distribution: churned vs retained")
    ax.set_xlabel("Tenure (months)")
    ax.set_ylabel("Customers")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "02_tenure_distribution.png"))
    plt.close(fig)
    print("\n  saved figures/02_tenure_distribution.png")

    # 2c. Churn rate across tenure buckets
    df["tenure_bucket"] = pd.cut(
        df["tenure_months"], [0, 6, 12, 24, 48, 72],
        labels=["0-6", "7-12", "13-24", "25-48", "49-72"],
    )
    s = df.groupby("tenure_bucket", observed=True)["churn_flag"].mean()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(s.index.astype(str), s.values, marker="o", color=DANGER, linewidth=2)
    ax.set_title("Churn rate falls sharply with tenure")
    ax.set_xlabel("Tenure bucket (months)")
    ax.set_ylabel("Churn rate")
    for i, v in enumerate(s.values):
        ax.text(i, v + 0.01, f"{v:.0%}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "03_churn_by_tenure_bucket.png"))
    plt.close(fig)
    print("  saved figures/03_churn_by_tenure_bucket.png")


# ----------------------------------------------------------------------
# 3. Model
# ----------------------------------------------------------------------
def build_model(df: pd.DataFrame):
    print("\n" + "=" * 64)
    print("3. PREDICTIVE MODEL (Logistic Regression)")
    print("=" * 64)

    target = "churn_flag"
    numeric = ["tenure_months", "monthly_charges", "total_charges", "senior_citizen"]
    categorical = ["partner", "dependents", "contract", "internet_service",
                   "online_security", "tech_support", "paperless_billing", "payment_method"]

    X = df[numeric + categorical]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical),
    ])
    model = Pipeline([
        ("pre", pre),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = roc_auc_score(y_test, proba)

    print(f"\nROC-AUC: {auc:.3f}\n")
    print(classification_report(y_test, pred, target_names=["Retained", "Churned"]))
    print("Confusion matrix [rows=actual, cols=predicted]:")
    print(confusion_matrix(y_test, pred))

    # ROC curve
    fpr, tpr, _ = roc_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(6, 5.5))
    ax.plot(fpr, tpr, color=ACCENT, lw=2, label=f"Logistic Regression (AUC={auc:.2f})")
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC curve — churn model")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "04_roc_curve.png"))
    plt.close(fig)
    print("\n  saved figures/04_roc_curve.png")

    return model, auc


def plot_drivers(model: Pipeline) -> pd.DataFrame:
    """Translate logistic-regression coefficients into odds ratios."""
    pre = model.named_steps["pre"]
    feat_names = pre.get_feature_names_out()
    coefs = model.named_steps["clf"].coef_[0]
    drivers = (
        pd.DataFrame({"feature": feat_names, "coef": coefs})
        .assign(odds_ratio=lambda d: np.exp(d["coef"]))
        .sort_values("coef")
    )
    # tidy feature names for the chart
    drivers["label"] = (drivers["feature"]
                        .str.replace("num__", "", regex=False)
                        .str.replace("cat__", "", regex=False))

    top = pd.concat([drivers.head(6), drivers.tail(6)])
    colors = [DANGER if c > 0 else ACCENT for c in top["coef"]]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["label"], top["coef"], color=colors)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_title("What drives churn (logistic-regression coefficients)\n"
                 "red = increases churn, blue = reduces churn")
    ax.set_xlabel("Coefficient (log-odds)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "05_churn_drivers.png"))
    plt.close(fig)
    print("  saved figures/05_churn_drivers.png")

    print("\nTop churn-INCREASING factors (odds ratio > 1):")
    print(drivers.tail(5)[["label", "odds_ratio"]].iloc[::-1]
          .to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nTop churn-REDUCING factors (odds ratio < 1):")
    print(drivers.head(5)[["label", "odds_ratio"]]
          .to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    return drivers


def recommendations() -> None:
    print("\n" + "=" * 64)
    print("4. BUSINESS RECOMMENDATIONS")
    print("=" * 64)
    print("""\
  1. Move month-to-month customers onto annual contracts — contract type is the
     single strongest churn lever. Offer a loyalty discount for switching.
  2. Protect the first 6 months. Churn is highest for new customers; invest in
     onboarding, early check-ins and a 90-day satisfaction touchpoint.
  3. Bundle tech support & online security. Customers with these add-ons churn
     markedly less — promote them, especially to fiber subscribers.
  4. Review fiber pricing / value. Fiber customers pay more and leave more; pair
     the premium with a clear value story or retention offer.
  5. Nudge electronic-check payers toward automatic payment methods, which
     correlate with lower churn.""")


def main() -> None:
    df = load_data()
    data_quality(df)
    plot_eda(df)
    model, _ = build_model(df)
    plot_drivers(model)
    recommendations()
    print("\nAll figures saved to figures/. Analysis complete.")


if __name__ == "__main__":
    main()
