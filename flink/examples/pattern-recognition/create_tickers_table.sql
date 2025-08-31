CREATE TABLE tickers (
    record_id BIGINT
    , symbol STRING
    , price DECIMAL(38, 2)
    , ts TIMESTAMP(3)
    , WATERMARK FOR ts AS ts - INTERVAL - '5' SECONDS
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'tickers'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'key.format' = 'csv'
    , 'key.fields' = 'record_id'
    , 'value.format' = 'json'
    , 'value.fields-include' = 'EXCEPT_KEY'
);
