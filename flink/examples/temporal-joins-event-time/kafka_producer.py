#!/usr/bin/env python3

import json
from datetime import datetime

from confluent_kafka import Producer

ORDER_ID = 1000

EXPECTED_INPUT_FMT = (
    "orders,<amount>,<currency> or "
    "currency,<rate>,<currency>"
)

TS_FMT = "%Y-%m-%d %H:%M:%S.%f"

producer = Producer({"bootstrap.servers": "localhost:9092"})

order_records = [
    {
        "key": 1,
        "value": {
            "order_id": 1,
            "currency": "EUR",
            "price": 10.0,
            "order_timestamp": "2025-08-26 08:00:00.000",
        }
    },
    {
        "key": 2,
        "value": {
            "order_id": 2,
            "currency": "EUR",
            "price": 20.0,
            "order_timestamp": "2025-08-26 12:00:00.000",
        }
    },
    {
        "key": 3,
        "value": {
            "order_id": 3,
            "currency": "EUR",
            "price": 30.0,
            "order_timestamp": "2025-08-26 14:00:00.000",
        }
    },
]

currency_records = [
    {
        "key": "EUR",
        "value": {
            "currency": "EUR",
            "conversion_rate": 1.0,
            "update_time": "2025-08-26 06:00:00.000"
        }
    },
    {
        "key": "USD",
        "value": {
            "currency": "USD",
            "conversion_rate": 1.0,
            "update_time": "2025-08-26 06:00:00.000"
        }
    },
    {
        "key": "EUR",
        "value": {
            "currency": "EUR",
            "conversion_rate": 1.1,
            "update_time": "2025-08-26 10:00:00.000"
        }
    },
    {
        "key": "USD",
        "value": {
            "currency": "USD",
            "conversion_rate": 1.0,
            "update_time": "2025-08-26 10:00:00.000"
        }
    },
    {
        "key": "EUR",
        "value": {
            "currency": "EUR",
            "conversion_rate": 1.4,
            "update_time": "2025-08-26 18:00:00.000"
        }
    },
    {
        "key": "USD",
        "value": {
            "currency": "USD",
            "conversion_rate": 1.4,
            "update_time": "2025-08-26 18:00:00.000"
        }
    },
]


def parse_input(inpt):
    """
    Order input: orders,<price>,<currency>
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
        global ORDER_ID
        ORDER_ID += 1
        amount, currency = value
        return "orders", {
            "key": currency,
            "value": {
                "order_id": ORDER_ID,
                "price": float(amount),
                "currency": currency,
                "order_timestamp": datetime.now().strftime(TS_FMT),
            }
        }

    elif topic == "currency":
        rate, currency = value
        return "currency", {
            "key": currency,
            "value": {
                "conversion_rate": float(rate),
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
    produce_messages("orders", order_records)
    produce_messages("currency", currency_records)
    producer.flush()
    print("Kafka records successfully sent")

    producer_user_input()


if __name__ == "__main__":
    main()
