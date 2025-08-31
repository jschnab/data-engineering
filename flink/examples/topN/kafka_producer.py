#!/usr/bin/env python3

import json
from datetime import datetime

from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})


def produce_messages(topic, messages):
    if not isinstance(messages, list):
        messages = [messages]
    for msg in messages:
        producer.produce(
            topic,
            key=str(msg["key"]),
            value=json.dumps(msg["value"]),
        )


def main():
    with open("records.json") as fi:
        records = json.load(fi)
    produce_messages("orders", records)
    producer.poll(1)
    producer.flush()


if __name__ == "__main__":
    main()
