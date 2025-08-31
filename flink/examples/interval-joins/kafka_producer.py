#!/usr/bin/env python3

import json

from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})

order_records = [
    {
        "key": 1,
        "value": {
            "order_id": 1,
            "order_timestamp": "2025-08-26 08:00:00.000",
        }
    },
    {
        "key": 2,
        "value": {
            "order_id": 2,
            "order_timestamp": "2025-08-26 12:00:00.000",
        }
    },
    {
        "key": 3,
        "value": {
            "order_id": 3,
            "order_timestamp": "2025-08-26 14:00:00.000",
        }
    },
]

shipment_records = [
    {
        "key": 1,
        "value": {
            "shipment_id": 1,
            "order_id": 2,
            "shipment_timestamp": "2025-08-26 15:12:34.123"
        }
    },
    {
        "key": 2,
        "value": {
            "shipment_id": 2,
            "order_id": 3,
            "shipment_timestamp": "2025-08-26 18:00:00.000"
        }
    },
    {
        "key": 3,
        "value": {
            "shipment_id": 3,
            "order_id": 1,
            "shipment_timestamp": "2025-08-26 19:23:45.678"
        }
    },
]


def produce_messages(topic, messages):
    for msg in messages:
        producer.produce(
            topic,
            key=str(msg["key"]),
            value=json.dumps(msg["value"]),
        )
    producer.poll(0.5)
    producer.flush()


def main():
    produce_messages("orders", order_records)
    produce_messages("shipments", shipment_records)
    producer.flush()
    print("Kafka records successfully sent")


if __name__ == "__main__":
    main()
