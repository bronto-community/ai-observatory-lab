"""catalog-api -- product listings."""

import logging
import random

from fastapi import FastAPI

from services.common import telemetry
from services.common.db import db

app = FastAPI(title="catalog-api")
telemetry.setup(app)
log = logging.getLogger("catalog-api")


@app.on_event("startup")
async def startup() -> None:
    telemetry.announce_release()


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}


@app.get("/items")
def items() -> dict:
    products = list(db().products.find({"active": True}).sort("rank", 1).limit(12))
    if random.random() < 0.3:
        log.warning("cache miss for shard %d, falling back to primary", random.randint(1, 8))
    return {"items": [p["sku"] for p in products]}
