-- Calculate monthly revenue and top products
WITH monthly_sales AS (
  SELECT
    DATE_TRUNC('month', order_date) AS month,
    product_id,
    SUM(quantity * unit_price) AS total_revenue,
    COUNT(*) AS order_count
  FROM orders
  WHERE order_date >= '2024-01-01'
  GROUP BY DATE_TRUNC('month', order_date), product_id
  HAVING SUM(quantity * unit_price) > 5000
)
SELECT
  ms.month,
  p.product_name,
  ms.total_revenue,
  ms.order_count,
  ROUND(ms.total_revenue / ms.order_count, 2) AS avg_order_value
FROM monthly_sales ms
INNER JOIN products p ON ms.product_id = p.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.status = 'active'
ORDER BY ms.month DESC, ms.total_revenue DESC
LIMIT 50;
