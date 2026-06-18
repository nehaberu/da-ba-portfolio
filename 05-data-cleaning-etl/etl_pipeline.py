"""
Data Cleaning & ETL Pipeline
============================
Takes a messy raw sales/CRM extract and turns it into a clean, analytics-ready
table — the unglamorous work that is ~80% of a real analyst's job.

Pipeline stages:
  EXTRACT  -> load raw_sales.csv
  PROFILE  -> "before" data-quality report (missing, dupes, bad types)
  TRANSFORM-> a sequence of documented, individually-logged cleaning steps
  VALIDATE -> assert the cleaned data meets quality rules
  LOAD     -> write clean_sales.csv + data_quality_report.txt

Each transform logs how many values it changed, so the cleaning is auditable.

Run:  python data/generate_messy_data.py
      python etl_pipeline.py
"""
import os
import re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw_sales.csv")
CLEAN = os.path.join(HERE, "data", "clean_sales.csv")
REPORT = os.path.join(HERE, "data_quality_report.txt")

MISSING_TOKENS = {"", " ", "n/a", "na", "null", "none", "-", "nan"}
COUNTRY_MAP = {
    "germany": "Germany", "de": "Germany", "deutschland": "Germany",
    "france": "France", "fr": "France",
    "uk": "UK", "united kingdom": "UK", "u.k.": "UK", "england": "UK",
    "netherlands": "Netherlands", "nl": "Netherlands", "the netherlands": "Netherlands",
    "spain": "Spain", "es": "Spain", "españa": "Spain",
}
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%B %d %Y"]

log_lines: list[str] = []


def log(msg: str) -> None:
    print(msg)
    log_lines.append(msg)


def to_missing(series: pd.Series) -> pd.Series:
    """Normalise the many spellings of 'missing' to real NaN."""
    return series.apply(
        lambda v: np.nan if (isinstance(v, str) and v.strip().lower() in MISSING_TOKENS)
        else (np.nan if pd.isna(v) else v)
    )


def parse_date(val):
    if pd.isna(val):
        return pd.NaT
    s = str(val).strip()
    for fmt in DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(s, errors="coerce")  # last-resort best effort


def parse_money(val):
    if pd.isna(val):
        return np.nan
    s = re.sub(r"[€$£\s]", "", str(val)).replace(",", "")
    try:
        return round(float(s), 2)
    except ValueError:
        return np.nan


def profile(df: pd.DataFrame, title: str) -> None:
    log(f"\n--- {title} ---")
    log(f"rows: {len(df):,}   columns: {df.shape[1]}")
    log(f"exact duplicate rows: {df.duplicated().sum()}")
    miss = df.isna().sum()
    miss = miss[miss > 0]
    if len(miss):
        log("missing values by column:")
        for col, n in miss.items():
            log(f"  {col:14s}: {n:>4} ({n/len(df):.1%})")
    else:
        log("missing values: none")


def main() -> None:
    if not os.path.exists(RAW):
        raise SystemExit("Run `python data/generate_messy_data.py` first.")

    # ---------------- EXTRACT ----------------
    log("=" * 64)
    log("ETL PIPELINE  |  raw_sales.csv -> clean_sales.csv")
    log("=" * 64)
    df = pd.read_csv(RAW, dtype=str)  # read everything as string to control parsing
    rows_in = len(df)

    # normalise missing tokens everywhere first so profiling is honest
    for col in df.columns:
        df[col] = to_missing(df[col])
    profile(df, "BEFORE cleaning")

    log("\n--- TRANSFORM steps ---")

    # 1. drop exact duplicates
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log(f"1. dropped {before - len(df)} exact duplicate rows")

    # 2. standardise country
    df["country"] = (df["country"].str.strip().str.lower().map(COUNTRY_MAP)
                     .where(df["country"].notna()))
    unmapped = df["country"].isna().sum()
    log(f"2. standardised country to 5 canonical values "
        f"({unmapped} left missing/unmapped)")

    # 3. parse dates from mixed formats
    df["order_date"] = df["order_date"].apply(parse_date)
    bad_dates = df["order_date"].isna().sum()
    log(f"3. parsed mixed date formats -> ISO datetime ({bad_dates} unparseable)")

    # 4. clean currency -> float
    df["unit_price"] = df["unit_price"].apply(parse_money)
    log("4. stripped currency symbols/separators from unit_price -> float")

    # 5. numeric coercion + range rules
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["customer_age"] = pd.to_numeric(df["customer_age"], errors="coerce")
    bad_qty = (df["quantity"] <= 0).sum()
    df.loc[df["quantity"] <= 0, "quantity"] = np.nan
    bad_age = ((df["customer_age"] < 18) | (df["customer_age"] > 100)).sum()
    df.loc[(df["customer_age"] < 18) | (df["customer_age"] > 100), "customer_age"] = np.nan
    log(f"5. enforced ranges: nulled {bad_qty} non-positive quantities, "
        f"{bad_age} impossible ages")

    # 6. tidy text: collapse whitespace, title-case names, lower-case emails
    df["customer_name"] = (df["customer_name"].str.strip()
                           .str.replace(r"\s+", " ", regex=True).str.title())
    df["email"] = df["email"].str.strip().str.lower()
    bad_email = (~df["email"].fillna("").str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")).sum()
    log(f"6. trimmed/normalised names & emails ({bad_email} emails fail format check)")

    # 7. derived column + impute prices by category median
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    med = df.groupby("category")["unit_price"].transform("median")
    n_imputed = df["unit_price"].isna().sum()
    df["unit_price"] = df["unit_price"].fillna(med).round(2)
    log(f"7. imputed {n_imputed} missing unit_price values with category median; "
        f"added revenue column")

    profile(df, "AFTER cleaning")

    # ---------------- VALIDATE ----------------
    log("\n--- VALIDATE (quality gates) ---")
    checks = {
        "no duplicate rows": df.duplicated().sum() == 0,
        "all countries canonical": set(df["country"].dropna()) <= set(COUNTRY_MAP.values()),
        "quantities positive or null": bool((df["quantity"].dropna() > 0).all()),
        "ages within 18-100 or null": bool(df["customer_age"].dropna().between(18, 100).all()),
        "dates parsed": df["order_date"].notna().mean() > 0.95,
    }
    for name, ok in checks.items():
        log(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    assert all(checks.values()), "Quality gate failed!"

    # ---------------- LOAD ----------------
    df.to_csv(CLEAN, index=False)
    completeness = 1 - df.isna().sum().sum() / df.size
    log(f"\nLOAD: wrote {CLEAN}")
    log(f"  rows in: {rows_in:,}  ->  rows out: {len(df):,}")
    log(f"  overall completeness: {completeness:.1%}")

    with open(REPORT, "w") as fh:
        fh.write("\n".join(log_lines) + "\n")
    print(f"\nData-quality report written to {REPORT}")


if __name__ == "__main__":
    main()
