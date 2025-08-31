SELECT
    window_start
    , window_end
    , COUNT(*) AS count_orders
FROM HOP(
    DATA => TABLE orders
    , TIMECOL => DESCRIPTOR(order_timestamp)
    , SLIDE => INTERVAL '1' MINUTES
    , SIZE => INTERVAL '5' MINUTES
)
GROUP BY window_start, window_end;
