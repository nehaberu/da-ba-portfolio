-- ============================================================
-- 01 | Schema overview & headline KPIs
-- ============================================================
-- The database has 4 tables:
--   customers(customer_id, signup_date, country, acquisition_channel)
--   products(product_id, product_name, category, unit_price)
--   orders(order_id, customer_id, order_date, channel, status)
--   order_items(order_item_id, order_id, product_id, quantity, unit_price)
--
-- Revenue convention used throughout: only orders with status = 'completed'
-- count toward revenue. Line revenue = quantity * unit_price.
-- ============================================================

-- Headline business KPIs in a single pass
WITH line_revenue AS (
    SELECT oi.order_id,
           oi.quantity * oi.unit_price AS line_total
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
)
SELECT
    ROUND(SUM(line_total), 2)                                AS total_revenue,
    COUNT(DISTINCT order_id)                                 AS completed_orders,
    ROUND(SUM(line_total) / COUNT(DISTINCT order_id), 2)     AS avg_order_value
FROM line_revenue;
