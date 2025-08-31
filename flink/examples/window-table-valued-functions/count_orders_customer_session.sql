SELECT
    window_start
    , window_end
    , customer_id
    , COUNT(*) AS count_orders
FROM SESSION(
    DATA => TABLE orders PARTITION BY customer_id
    , TIMECOL => DESCRIPTOR(order_timestamp)
    , GAP => INTERVAL '5' MINUTES
)
GROUP BY window_start, window_end;
