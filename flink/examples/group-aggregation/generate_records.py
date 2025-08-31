import json
import random
from datetime import datetime, timedelta

SUPPLIERS = [
    "Amazon",
    "Walmart",
    "Target",
    "Whatnot",
]

PRODUCT_CATEGORY = [
    "Sports cards",
    "Video games",
    "Fashion",
    "Cycling",
    "Spirits",
]

records = []

now = datetime.now()

for order_id in range(1, 500):
    records.append(
        {
            "key": order_id,
            "value": {
                "order_id": order_id,
                "product_category": random.choice(PRODUCT_CATEGORY),
                "supplier": random.choice(SUPPLIERS),
                "amount": random.randint(1, 10),
                "rating": random.randint(1, 5),
                "order_timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            },
        }
    )
    now += timedelta(
        seconds=random.randint(1, 20),
        microseconds=random.randint(1, 999_999),
    )

with open("records.json", "w") as fi:
    json.dump(records, fi)
