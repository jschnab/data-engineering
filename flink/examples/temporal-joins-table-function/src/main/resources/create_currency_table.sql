CREATE TABLE currency (
    currency STRING
    , rate DECIMAL(32,2)
    , update_time TIMESTAMP(3)
    , WATERMARK FOR update_time AS update_time - INTERVAL - '5' SECONDS
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'currency'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'value.format' = 'json'
);
