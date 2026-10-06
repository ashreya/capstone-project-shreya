-- Order totals
SELECT
COUNT(*) AS total_orders,
ROUND(SUM(o.quantity*p.price*(1-COALESCE(o.discount_pct,0)/100)),2) AS total_revenue,
ROUND(SUM(o.quantity*p.price*(1-COALESCE(o.discount_pct,0)/100))/COUNT(*),2) AS avg_order_value
FROM
orders o
LEFT JOIN
products p
ON
o.product_id = p.product_id;


-- COUNT(*) VS COUNT(column)
SELECT 
COUNT(*) AS total_orders,
COUNT(rating) AS total_orders_rated,
COUNT(*) - COUNT(rating) as difference
from orders;


-- LEFT JOIN with genuine zero-match row
SELECT
c.customer_id,
c.name
FROM 
customers c
LEFT JOIN
orders o 
ON
c.customer_id = o.customer_id
group by c.customer_id
HAVING COUNT(o.order_id)=0;

SELECT
c.customer_id,
c.name
FROM
customers c
WHERE
c.customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- Group By + Having
SELECT
COUNT(*) AS total_orders,
SUM(o.returned) AS returned_orders,
ROUND((SUM(o.returned)/COUNT(*)) * 100.0,1) AS return_rate_pct
FROM
orders o JOIN customers c
ON
o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- Ranking with ORDER BY + LIMIT/ OFFSET
SELECT
c.customer_id,
c.name,
ROUND(SUM(o.quantity*p.price*(1-COALESCE(o.discount_pct,0)/100)),2) AS total_spend
FROM
customers c
INNER JOIN
orders o
INNER JOIN
products p
ON c.customer_id = o.customer_id AND p.product_id = o.product_id
GROUP BY c.customer_id
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;
-- tie-breaker matters because if 2 customers have same spendings then their order is deterministic and not random 
SELECT
c.customer_id,
c.name,
ROUND(SUM(o.quantity*p.price*(1-COALESCE(o.discount_pct,0)/100)),2) AS total_spend
FROM
customers c
INNER JOIN
orders o
INNER JOIN
products p
ON c.customer_id = o.customer_id AND p.product_id = o.product_id
GROUP BY c.customer_id
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3
OFFSET 2;

-- Three Table Join with Grooup by
SELECT
p.category as category,
COUNT(*) AS order_count,
ROUND(SUM(o.quantity*p.price*(1-COALESCE(o.discount_pct,0)/100)),2) AS category_revenue
FROM
orders o 
INNER JOIN
products p
INNER JOIN
customers c
ON o.customer_id = c.customer_id AND p.product_id = o.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- like pattern matching
SELECT
customer_id,
name
FROM customers
WHERE name LIKE "A%";

-- DISTINCT
SELECT
DISTINCT acquisition_source 
FROM customers
ORDER BY acquisition_source ASC;

-- ALTER TABLE + UPDATE with CASE
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

SELECT * from customers;

SET SQL_SAFE_UPDATES = 0;
UPDATE customers
SET loyalty_tier = CASE WHEN city_tier = 1 THEN "Gold" ELSE "Silver" END;
UPDATE customers
SET loyalty_tier = "Silver" WHERE loyalty_tier = "SILVER";
SELECT loyalty_tier, COUNT(*) FROM customers GROUP BY loyalty_tier; 

SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;