CREATE TABLE mytable (message STRING)
WITH (
    'connector' = 'kafka'
    , 'topic' = 'flink-ml-test'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'value.format' = 'json'
);
