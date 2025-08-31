#!/usr/bin/env python3

import json
from datetime import datetime

from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})

records = [
    {
        "key": None,
        "value": {"message": "Hello, world!"},
    },
    {
        "key": None,
        "value": {"message": "There is no love!"},
    },
]


def produce_messages(topic, messages):
    if not isinstance(messages, list):
        messages = [messages]
    for msg in messages:
        producer.produce(
            topic,
            key=str(msg["key"]),
            value=json.dumps(msg["value"]),
        )
    producer.poll(0.5)
    producer.flush()


def main():
    produce_messages("flink-ml-test", records)
    print("Kafka records successfully sent")


if __name__ == "__main__":
    main()
