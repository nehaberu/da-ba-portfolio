-- ============================================================
-- 05 | Monthly cohort retention
-- ============================================================
-- Group customers by the month of their FIRST order (their cohort),
-- then measure how many are still ordering N months later.
-- This is the single most-requested "advanced SQL" interview task
-- for analyst roles at subscription / e-commerce companies.
--
-- Technique: self-join via first-order CTE, month arithmetic,
-- and a pivoted retention curve.
-- ============================================================

WITH first_order AS (
    SELECT
        customer_id,
        MIN(strftime('%Y-%m', order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
activity AS (
    SELECT
        f.cohort_month,
        f.customer_id,
        -- whole months between the cohort month and the activity month
        (CAST(strftime('%Y', o.order_date) AS INT) - CAST(substr(f.cohort_month,1,4) AS INT)) * 12
        + (CAST(strftime('%m', o.order_date) AS INT) - CAST(substr(f.cohort_month,6,2) AS INT)) AS month_offset
    FROM orders o
    JOIN first_order f ON f.customer_id = o.customer_id
    WHERE o.status = 'completed'
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS n FROM first_order GROUP BY cohort_month
)
SELECT
    a.cohort_month,
    cs.n AS cohort_size,
    a.month_offset,
    COUNT(DISTINCT a.customer_id)                                  AS active_customers,
    ROUND(100.0 * COUNT(DISTINCT a.customer_id) / cs.n, 1)         AS retention_pct
FROM activity a
JOIN cohort_size cs ON cs.cohort_month = a.cohort_month
WHERE a.month_offset BETWEEN 0 AND 6
GROUP BY a.cohort_month, a.month_offset, cs.n
ORDER BY a.cohort_month, a.month_offset;
