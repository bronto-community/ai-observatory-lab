"""The shop's MongoDB Atlas database, shared by catalog-api and checkout-api.

Opened on first use, after telemetry.setup(): the pymongo instrumentation only
sees clients created once it is installed.
"""

import functools
import os

from pymongo import MongoClient


@functools.cache
def db():
    client = MongoClient(
        os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
        appname=os.environ.get("SERVICE_NAME", "storefront"),
        maxPoolSize=int(os.environ.get("MONGODB_POOL_SIZE", "20")),
        serverSelectionTimeoutMS=5000,
    )
    return client[os.environ.get("MONGODB_DB", "storefront")]
