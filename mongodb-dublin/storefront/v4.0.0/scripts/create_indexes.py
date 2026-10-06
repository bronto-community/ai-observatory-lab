"""Create the indexes the services rely on. Run once per environment:

    MONGODB_URI=... python scripts/create_indexes.py
"""

import os

from pymongo import ASCENDING, DESCENDING, MongoClient

db = MongoClient(os.environ["MONGODB_URI"])[os.environ.get("MONGODB_DB", "storefront")]

# catalog-api: the listing page
db.products.create_index([("active", ASCENDING), ("rank", ASCENDING)])
db.products.create_index("sku", unique=True)

# checkout-api: order lookups by id, a customer's orders, and reporting by day
db.orders.create_index("order_id", unique=True)
db.orders.create_index([("customer_id", ASCENDING), ("created_at", DESCENDING)])
db.orders.create_index("created_at")

print("indexes:", {c: [i["name"] for i in db[c].list_indexes()] for c in ("products", "orders")})
