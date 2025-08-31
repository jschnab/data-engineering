CREATE TABLE orders (
    amount DECIMAL(32, 2)
    , currency STRING
    , processing_ts AS PROCTIME()
    , WATERMARK processing_ts AS processing_ts - INTERVAL '5' SECONDS
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'orders'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'value.format' = 'json'
);
