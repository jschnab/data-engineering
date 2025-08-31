import json
import random
from datetime import datetime, timedelta

SYMBOLS = ["TJX", "BX", "KR"]

PRICES = {
    "TJX": 136.61,
    "BX": 171.4,
    "KR": 67.84
}

records = []

now = datetime.now()

for record_id in range(1, 1000):
    symbol = random.choice(SYMBOLS)
    records.append(
        {
            "key": record_id,
            "value": {
                "symbol": symbol,
                "price": PRICES[symbol],
                "ts": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            },
        }
    )
    sign = 1 if random.random() > 0.5 else -1
    PRICES[symbol] += sign * random.random()
    now += timedelta(
        seconds=random.randint(1, 20),
        microseconds=random.randint(1, 999_999),
    )

with open("records.json", "w") as fi:
    json.dump(records, fi)
