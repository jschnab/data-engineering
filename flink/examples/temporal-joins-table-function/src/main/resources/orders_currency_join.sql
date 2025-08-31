SELECT
    orders.currency
    , amount * rate AS converted_amount
    , amount
    , order_time
    , rate
    , update_time
FROM
  orders,
  LATERAL TABLE (rates(order_time)) r
WHERE r.currency = orders.currency
