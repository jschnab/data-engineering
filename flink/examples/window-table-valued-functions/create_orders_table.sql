CREATE TABLE orders (
    order_id INTEGER
    , customer_id INTEGER
    , amount INTEGER
    , item STRING
    , order_timestamp TIMESTAMP(3)
    , WATERMARK FOR order_timestamp AS order_timestamp - INTERVAL - '5' SECONDS
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
