SELECT o.order_id, o.total, c.country, c.zip
FROM orders AS o
JOIN customers FOR SYSTEM_TIME AS OF o.order_timestamp AS c
ON o.customer_id = c.id;
