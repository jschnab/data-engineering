SELECT
    supplier
    , product_category
    , rating
    , COUNT(*)
FROM orders
GROUP BY CUBE (supplier, product_category, rating)
;
