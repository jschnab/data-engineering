CREATE TABLE currency (
    k_currency STRING
    , conversion_rate DECIMAL(32,2)
    , update_time TIMESTAMP(3)
    , WATERMARK FOR update_time AS update_time - INTERVAL - '5' SECONDS
    , PRIMARY KEY (k_currency) NOT ENFORCED
) WITH (
    'connector' = 'upsert-kafka' -- this connector produces versioned tables, unlike the normal kafka connector
    , 'topic' = 'currency'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'key.format' = 'raw'
    , 'key.fields-prefix' = 'k_'
    , 'value.format' = 'json'
    , 'value.fields-include' = 'EXCEPT_KEY'
);
