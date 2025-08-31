CREATE TABLE orders (
    order_id INTEGER
    , price DECIMAL(32, 2)
    , currency STRING
    , order_timestamp TIMESTAMP(3)
    , WATERMARK FOR order_timestamp AS order_timestamp - INTERVAL - '5' SECONDS
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'orders'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'value.format' = 'json'
);
