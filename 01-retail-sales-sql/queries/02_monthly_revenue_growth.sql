-- ============================================================
-- 02 | Monthly revenue trend + Month-over-Month growth
-- ============================================================
-- Technique: aggregation by month, then a window function (LAG)
-- to compare each month against the previous one.
-- Business question: "Is revenue growing, and how fast?"
-- ============================================================

WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date)        AS month,
        SUM(oi.quantity * oi.unit_price)       AS revenue,
        COUNT(DISTINCT o.order_id)             AS orders
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2)                                                   AS revenue,
    orders,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2)                        AS prev_month_revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
                 / LAG(revenue) OVER (ORDER BY month), 1)               AS mom_growth_pct
FROM monthly
ORDER BY month;
