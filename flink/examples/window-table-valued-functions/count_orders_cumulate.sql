SELECT
    window_start
    , window_end
    , COUNT(*) AS count_orders
FROM CUMULATE(
    DATA => TABLE orders
    , TIMECOL => DESCRIPTOR(order_timestamp)
    , STEP => INTERVAL '1' MINUTES
    , SIZE => INTERVAL '60' MINUTES
)
GROUP BY window_start, window_end;
