SELECT
  amount, rate
FROM
  orders,
  LATERAL TABLE (rates(orders.processing_ts))
WHERE
  k_currency = currency
;
