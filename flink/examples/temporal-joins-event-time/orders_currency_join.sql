SELECT 
     order_id
     , price
     , conversion_rate
     , price * conversion_rate as converted_price
     , orders.currency
     , order_timestamp
     , update_time
FROM orders
LEFT JOIN currency FOR SYSTEM_TIME AS OF orders.order_timestamp
ON orders.currency = currency.k_currency
;
