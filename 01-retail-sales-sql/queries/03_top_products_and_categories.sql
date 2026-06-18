-- ============================================================
-- 03 | Top products & category performance (with ranking)
-- ============================================================
-- Technique: JOIN to bring in product attributes, aggregate,
-- RANK() window function, and category revenue share.
-- Business question: "What sells, and where is revenue concentrated?"
-- ============================================================

-- 3a. Top 10 products by revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity)                              AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)    AS revenue,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS revenue_rank
FROM order_items oi
JOIN orders o   ON o.order_id   = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- 3b. Category share of total revenue (Pareto view)
WITH cat AS (
    SELECT
        p.category,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id   = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.status = 'completed'
    GROUP BY p.category
)
SELECT
    category,
    ROUND(revenue, 2)                                              AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1)              AS pct_of_total,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
                / SUM(revenue) OVER (), 1)                         AS cumulative_pct
FROM cat
ORDER BY revenue DESC;
