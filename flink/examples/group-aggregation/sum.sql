SELECT
    product_category
    , SUM(amount) AS total_amount
FROM orders
GROUP BY product_category
;
