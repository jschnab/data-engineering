SELECT
    window_start
    , window_end
    , COUNT(*) AS count_orders
FROM TUMBLE(
    DATA => TABLE orders
    , TIMECOL => DESCRIPTOR(order_timestamp)
    , SIZE => INTERVAL '1' MINUTES
)
GROUP BY window_start, window_end;
