import json
import random
from datetime import datetime, timedelta

LIVESTREAM_ID = list(range(10))

records = []

now = datetime.now()

for order_id in range(1, 500):
    records.append(
        {
            "key": order_id,
            "value": {
                "livestream_id": random.choice(LIVESTREAM_ID),
                "order_id": order_id,
                "price": random.randint(1, 100),
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
