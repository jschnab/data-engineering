SELECT
    order_id
    , livestream_id
    , price
    , order_timestamp
FROM (
    SELECT
        *
        , ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY order_timestamp
        ) AS row_num
    FROM orders
)
WHERE row_num = 1
;
