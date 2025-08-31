#!/usr/bin/env python3

import json
import sys
from datetime import datetime

from confluent_kafka import Producer

EXPECTED_INPUT_FMT = "orders,<total>,<customer-id>"
TS_FMT = "%Y-%m-%d %H:%M:%S.%f"
ORDER_ID = 1000

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
    producer.poll(0.5)
    producer.flush()


def parse_input(inpt):
    """
    Order input: orders,<total>,<customer-id>
    E.g.: order,100.0,1
    """
    global ORDER_ID
    ORDER_ID += 1

    split = inpt.split(",")
    if len(split) != 3:
        raise ValueError(
            f"Invalid input: '{inpt}'.\n"
            f"Expected format: {EXPECTED_INPUT_FMT}"
        )

    topic, *value = split

    if topic == "orders":
        total, customer_id = value
        return "orders", {
            "key": str(ORDER_ID),
            "value": {
                "total": float(total),
                "customer_id": customer_id,
                "order_timestamp": datetime.now().strftime(TS_FMT),
            }
        }

    else:
        raise ValueError(
            f"Unexpected topic: '{topic}'.\n"
            f"Expected format: {EXPECTED_INPUT_FMT}"
        )


def producer_user_input():
    print(f"Expected format: {EXPECTED_INPUT_FMT}")
    while True:
        inpt = input("Input: ").strip()
        if inpt == "":
            print("No more input")
            break
        else:
           try:
               topic, msg = parse_input(inpt)
               produce_messages(topic, msg)
               print("Kafka record successfully sent")
           except (ValueError, TypeError) as err:
               print(err)

    producer.flush()


def main():
    producer_user_input()
    producer.flush()


if __name__ == "__main__":
    main()
