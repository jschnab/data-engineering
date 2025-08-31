SELECT
    *
    , ROW_NUMBER() OVER (
        PARTITION BY window_start, window_end
        ORDER BY gmv DESC
    ) AS rownum
FROM (
    SELECT
        window_start
        , window_end
        , livestream_id
        , SUM(price) AS gmv
        , COUNT(*) AS cnt
    FROM TUMBLE(TABLE orders, DESCRIPTOR(order_timestamp), INTERVAL '10' MINUTES)
    GROUP BY window_start, window_end, livestream_id
)
QUALIFY rownum <= 3;
