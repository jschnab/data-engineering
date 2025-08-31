CREATE TABLE orders (
    amount DECIMAL(32, 2)
    , currency STRING
    , order_time TIMESTAMP(3)
    , WATERMARK FOR order_time AS order_time - INTERVAL '5' SECONDS
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'orders'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'value.format' = 'json'
);
