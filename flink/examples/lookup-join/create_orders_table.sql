CREATE TABLE orders (
    order_id BIGINT
    , total DECIMAL(32, 2)
    , customer_id INT
    , proc_time as PROCTIME()
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'orders'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'key.format' = 'csv'
    , 'key.fields' = 'order_id'
    , 'value.format' = 'json'
    , 'value.fields-include' = 'EXCEPT_KEY'
);
