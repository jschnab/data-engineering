SELECT
    product_category
    , SUM(amount) OVER(
        PARTITION BY product_category
        ORDER BY order_timestamp
    )
FROM orders
;
