#!/usr/bin/env python3

import json
import sys
from datetime import datetime

from confluent_kafka import Producer

EXPECTED_INPUT_FMT = (
    "orders,<amount>,<currency> or "
    "currency,<rate>,<currency>"
)

TS_FMT = "%Y-%m-%d %H:%M:%S.%f"


producer = Producer({"bootstrap.servers": "localhost:9092"})

currency_records = [
    {
        "key": "EUR",
        "value": {
            "currency": "EUR",
            "rate": 1.0,
            "update_time": "2025-08-26 00:00:00.000",
        }
    },
    {
        "key": "USD",
        "value": {
            "currency": "USD",
            "rate": 1.0,
            "update_time": "2025-08-26 00:00:00.000",
        }
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


def parse_input(inpt):
    """
    Order input: orders,<amount>,<currency>
    E.g.: order,100.0,EUR

    Currency input: currency,<rate>,<currency>
    E.g.: currency,1.23,EUR
    """

    split = inpt.split(",")
    if len(split) != 3:
        raise ValueError(
            f"Invalid input: '{inpt}'.\n"
            f"Expected format: {EXPECTED_INPUT_FMT}"
        )

    topic, *value = split

    if topic == "orders":
        amount, currency = value
        return "orders", {
            "key": currency,
            "value": {
                "amount": float(amount),
                "currency": currency,
            }
        }

    elif topic == "currency":
        rate, currency = value
        return "currency", {
            "key": currency,
            "value": {
                "rate": float(rate),
                "currency": currency,
                "update_time": datetime.now().strftime(TS_FMT),
            }
        }

    else:
        raise ValueError(
            f"Unexpected topic: '{topic}'.\n"
            f"Expected format: {EXPECTED_INPUT_FMT}"
        )


def main():
    produce_messages("currency", currency_records)

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


if __name__ == "__main__":
    main()
