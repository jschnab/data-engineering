SELECT
    supplier
    , product_category
    , rating
    , COUNT(*)
FROM orders
GROUP BY GROUPING SETS (
    (supplier, rating)
    , (supplier)
    , (rating)
    , ()
)
;
