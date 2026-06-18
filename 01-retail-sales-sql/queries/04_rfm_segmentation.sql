-- ============================================================
-- 04 | RFM customer segmentation
-- ============================================================
-- RFM = Recency, Frequency, Monetary. A classic CRM technique to
-- group customers by value and engagement so marketing can target
-- the right people (e.g. win back "At Risk", reward "Champions").
--
-- Technique: CTEs + NTILE() to bucket each metric into quintiles,
-- then a CASE expression to label segments.
-- Recency is measured against the latest order date in the dataset.
-- ============================================================

WITH bounds AS (
    SELECT MAX(order_date) AS max_date FROM orders WHERE status = 'completed'
),
customer_rfm AS (
    SELECT
        o.customer_id,
        CAST(julianday((SELECT max_date FROM bounds)) - julianday(MAX(o.order_date)) AS INT) AS recency_days,
        COUNT(DISTINCT o.order_id)                       AS frequency,
        SUM(oi.quantity * oi.unit_price)                 AS monetary
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY o.customer_id
),
scored AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        ROUND(monetary, 2) AS monetary,
        -- lower recency = better, so reverse the ordering for R
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency  ASC)   AS f_score,
        NTILE(5) OVER (ORDER BY monetary   ASC)   AS m_score
    FROM customer_rfm
)
SELECT
    customer_id,
    recency_days, frequency, monetary,
    r_score, f_score, m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3                  THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2                  THEN 'New / Promising'
        WHEN r_score <= 2 AND f_score >= 4                  THEN 'At Risk (high value)'
        WHEN r_score <= 2 AND f_score <= 2                  THEN 'Hibernating'
        ELSE 'Needs Attention'
    END AS segment
FROM scored
ORDER BY monetary DESC
LIMIT 25;
