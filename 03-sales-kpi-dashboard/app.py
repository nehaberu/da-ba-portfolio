"""
Sales KPI Dashboard
===================
An interactive Streamlit dashboard over a Superstore-style sales dataset.
Sidebar filters (date range, region, segment, category) drive KPI cards,
trend lines and breakdown charts — the kind of self-serve BI tool a Business
Analyst builds so stakeholders can answer their own questions.

Run:  python data/generate_sales.py      # build data/sales.csv first
      streamlit run app.py
"""
import os
import numpy as np
import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "sales.csv")

st.set_page_config(page_title="Sales KPI Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    return df


def kpi_card(col, label, value, delta=None):
    col.metric(label, value, delta)


def main() -> None:
    if not os.path.exists(DATA):
        st.error("data/sales.csv not found. Run `python data/generate_sales.py` first.")
        st.stop()

    df = load_data()

    # ---------------- Sidebar filters ----------------
    st.sidebar.header("Filters")
    dmin, dmax = df["order_date"].min().date(), df["order_date"].max().date()
    date_range = st.sidebar.date_input("Date range", (dmin, dmax),
                                       min_value=dmin, max_value=dmax)
    regions = st.sidebar.multiselect("Region", sorted(df.region.unique()),
                                     default=sorted(df.region.unique()))
    segments = st.sidebar.multiselect("Segment", sorted(df.segment.unique()),
                                      default=sorted(df.segment.unique()))
    categories = st.sidebar.multiselect("Category", sorted(df.category.unique()),
                                        default=sorted(df.category.unique()))

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        start, end = pd.Timestamp(dmin), pd.Timestamp(dmax)

    mask = (
        df.order_date.between(start, end)
        & df.region.isin(regions or df.region.unique())
        & df.segment.isin(segments or df.segment.unique())
        & df.category.isin(categories or df.category.unique())
    )
    d = df[mask]

    # ---------------- Header + KPIs ----------------
    st.title("📊 Sales KPI Dashboard")
    st.caption(f"{start.date()} → {end.date()}  |  {len(d):,} order lines")

    if d.empty:
        st.warning("No data for the selected filters.")
        st.stop()

    total_sales = d.sales.sum()
    total_profit = d.profit.sum()
    margin = total_profit / total_sales if total_sales else 0
    aov = total_sales / d.order_id.nunique()

    # period-over-period delta: compare latest full month vs previous
    monthly = d.groupby("month")["sales"].sum().sort_index()
    mom = None
    if len(monthly) >= 2 and monthly.iloc[-2] != 0:
        mom = f"{(monthly.iloc[-1] / monthly.iloc[-2] - 1) * 100:.1f}% MoM"

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Total Sales", f"€{total_sales:,.0f}", mom)
    kpi_card(c2, "Total Profit", f"€{total_profit:,.0f}")
    kpi_card(c3, "Profit Margin", f"{margin:.1%}")
    kpi_card(c4, "Avg Order Value", f"€{aov:,.0f}")

    st.divider()

    # ---------------- Trend ----------------
    st.subheader("Monthly sales & profit trend")
    trend = d.groupby("month")[["sales", "profit"]].sum()
    st.line_chart(trend, height=320)

    # ---------------- Breakdowns ----------------
    left, right = st.columns(2)
    with left:
        st.subheader("Sales by category")
        by_cat = d.groupby("category")["sales"].sum().sort_values(ascending=False)
        st.bar_chart(by_cat, height=300)
    with right:
        st.subheader("Profit by region")
        by_reg = d.groupby("region")["profit"].sum().sort_values(ascending=False)
        st.bar_chart(by_reg, height=300)

    # ---------------- Profitability watch-out ----------------
    st.subheader("⚠️ Margin by sub-category (watch the loss-makers)")
    sub = (d.groupby("sub_category")
             .agg(sales=("sales", "sum"), profit=("profit", "sum"))
             .assign(margin=lambda x: x.profit / x.sales)
             .sort_values("margin"))
    sub_display = sub.copy()
    sub_display["sales"] = sub_display["sales"].map("€{:,.0f}".format)
    sub_display["profit"] = sub_display["profit"].map("€{:,.0f}".format)
    sub_display["margin"] = sub_display["margin"].map("{:.1%}".format)
    st.dataframe(sub_display, use_container_width=True)

    # ---------------- Top discount-driven loss check ----------------
    with st.expander("How discount level affects profit"):
        disc = (d.groupby("discount")
                  .agg(orders=("order_id", "count"),
                       avg_profit=("profit", "mean"))
                  .reset_index())
        disc["discount"] = (disc["discount"] * 100).map("{:.0f}%".format)
        st.bar_chart(disc.set_index("discount")["avg_profit"], height=280)
        st.caption("Average profit per order line at each discount tier — "
                   "deep discounts erode and can reverse profitability.")


if __name__ == "__main__":
    main()
