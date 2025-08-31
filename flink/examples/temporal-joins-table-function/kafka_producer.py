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
        "key": "JPY",
        "value": {
            "update_time": "2025-08-26 09:00:00.000",
            "currency": "JPY",
            "rate": 102.0,
        }
    },
    {
        "key": "EUR",
        "value": {
            "update_time": "2025-08-26 09:00:00.000",
            "currency": "EUR",
            "rate": 114.0,
        }
    },
    {
        "key": "USD",
        "value": {
            "update_time": "2025-08-26 09:00:00.000",
            "currency": "USD",
            "rate": 1.0,
        }
    },
    {
        "key": "EUR",
        "value": {
            "update_time": "2025-08-26 11:15:00.000",
            "currency": "EUR",
            "rate": 119.0,
        }
    },
    {
        "key": "GBP",
        "value": {
            "update_time": "2025-08-26 11:49:00.000",
            "currency": "GBP",
            "rate": 108.0,
        }
    },
]

orders_records = [
    {
        "key": "EUR",
        "value": {
            "order_time": "2025-08-26 10:15:00.000",
            "amount": 2.0,
            "currency": "EUR",
        }
    },
    {
        "key": "USD",
        "value": {
            "order_time": "2025-08-26 10:30:00.000",
            "amount": 1.0,
            "currency": "USD",
        }
    },
    {
        "key": "JPY",
        "value": {
            "order_time": "2025-08-26 10:32:00.000",
            "amount": 50.0,
            "currency": "JPY",
        }
    },
    {
        "key": "EUR",
        "value": {
            "order_time": "2025-08-26 10:52:00.000",
            "amount": 3.0,
            "currency": "EUR",
        }
    },
    {
        "key": "USD",
        "value": {
            "order_time": "2025-08-26 11:04:00.000",
            "amount": 5.0,
            "currency": "USD",
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
                "order_time": datetime.now().strftime(TS_FMT),
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
    for rec in currency_records:
        produce_messages("currency", rec)
    for rec in orders_records:
        produce_messages("orders", rec)
    producer.flush()

    producer_user_input()


if __name__ == "__main__":
    main()
