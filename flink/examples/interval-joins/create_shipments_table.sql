CREATE TABLE shipments (
    shipment_id INTEGER
    , order_id INTEGER
    , shipment_timestamp TIMESTAMP(3)
    , WATERMARK FOR shipment_timestamp AS shipment_timestamp - INTERVAL - '5' SECONDS
) WITH (
    'connector' = 'kafka'
    , 'topic' = 'shipments'
    , 'properties.bootstrap.servers' = 'localhost:9092'
    , 'scan.startup.mode' = 'earliest-offset'
    , 'value.format' = 'json'
);
