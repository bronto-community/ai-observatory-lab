"""Fill the shop's database once: 40 products and ~1.5M past orders.

The orders are what make a missing index hurt: a query that can't use one
scans all of them. Safe to re-run; it tops up to the target and stops.
"""

import datetime
import os
import random
import uuid

from pymongo import MongoClient

db = MongoClient(os.environ["MONGODB_URI"])[os.environ.get("MONGODB_DB", "storefront")]
TARGET = int(os.environ.get("SEED_ORDERS", "1500000"))
CUSTOMERS = int(os.environ.get("SEED_CUSTOMERS", "50000"))

if db.products.estimated_document_count() == 0:
    db.products.insert_many([
        {"sku": f"sku-{i}", "name": f"Dino figure #{i}", "rank": i, "active": i <= 36, "price": 1200 + 100 * i}
        for i in range(1, 41)
    ])

have = db.orders.estimated_document_count()
now = datetime.datetime.now(datetime.timezone.utc)
while have < TARGET:
    batch = []
    for _ in range(min(10_000, TARGET - have)):
        n = random.randint(1, CUSTOMERS)
        batch.append({
            "order_id": str(uuid.uuid4()),
            "customer_id": f"c{n}",
            "customer_email": f"customer{n}@example.com",
            "items": [f"sku-{random.randint(1, 40)}" for _ in range(random.randint(1, 3))],
            "total": random.randint(1200, 9000),
            "created_at": now - datetime.timedelta(minutes=random.randint(1, 60 * 24 * 365)),
        })
    db.orders.insert_many(batch, ordered=False)
    have += len(batch)
    print(f"orders: {have}/{TARGET}", flush=True)
print("seeded")
