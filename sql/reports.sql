-- Order totals
--  (180, 99860.20, 554.78)
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
-- (180, 165, 15)
SELECT 
COUNT(*) AS total_orders,
COUNT(rating) AS total_orders_rated,
COUNT(*) - COUNT(rating) as difference
from orders;


-- LEFT JOIN with genuine zero-match row
-- (C045,Vihaan)
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

-- C045, Vihaan
SELECT
c.customer_id,
c.name
FROM
customers c
WHERE
c.customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- Group By + Having
-- (Jaipur,	19,	8,	42.1)
-- (Lucknow, 49, 15, 30.6)
-- (Bangalore,	33,	8,	24.2)
SELECT
c.city,
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
-- (C043, Reyansh, 12920.00)
-- (C026, Isha, 8371.60)
-- (C008, Meera, 4564.60)
-- (C011, Arjun, 4111.00)
-- (C042, Sanya, 3785.00)
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

-- (C008, Meera, 4564.60)
-- (C011, Arjun, 4111.00)
-- (C042, Sanya, 3785.00)
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
-- (Haircare, 54, 44956.10)
-- (Skincare, 60, 27346.00)
-- (Babycare, 30, 16805.00)
-- (PersonalCare, 36, 10753.10)
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
-- C001	Aarav
-- C003	Aditi
-- C004	Ananya
-- C011	Arjun
-- C021	Aryan
-- C030	Anika
-- C031	Aditya
-- C036	Aisha
-- C041	Ayaan
-- C044	Aria
SELECT
customer_id,
name
FROM customers
WHERE name LIKE "A%";

-- DISTINCT
-- (Ad,Organic,Referral,Social)
SELECT
DISTINCT acquisition_source 
FROM customers
ORDER BY acquisition_source ASC;

-- ALTER TABLE + UPDATE with CASE
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

SET SQL_SAFE_UPDATES = 0;
UPDATE customers
SET loyalty_tier = CASE WHEN city_tier = 1 THEN "Gold" ELSE "Silver" END;
UPDATE customers
SET loyalty_tier = "Silver" WHERE loyalty_tier = "SILVER";

-- (Gold, 28)
-- (Silver, 17)
SELECT loyalty_tier, COUNT(*) FROM customers GROUP BY loyalty_tier; 
