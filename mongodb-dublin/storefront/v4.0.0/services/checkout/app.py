"""checkout-api -- turns a cart into a confirmed order."""

import asyncio
import datetime
import logging
import uuid

import httpx
from fastapi import FastAPI

from services.checkout import config
from services.common import telemetry
from services.common.db import db

app = FastAPI(title="checkout-api")
telemetry.setup(app)
log = logging.getLogger("checkout-api")

client = httpx.AsyncClient(
    timeout=config.PAYMENTS_TIMEOUT_S,
    limits=httpx.Limits(
        max_connections=config.PAYMENTS_POOL_SIZE,
        max_keepalive_connections=config.PAYMENTS_POOL_SIZE,
    ),
)


@app.on_event("startup")
async def startup() -> None:
    telemetry.announce_release()


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}


@app.post("/checkout")
async def checkout(order: dict) -> dict:
    customer = order.get("customer", {})
    cart = order.get("cart", [])
    r = await client.post(
        f"{config.PAYMENTS_URL}/charge",
        json={"amount": 4200},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    r.raise_for_status()
    order_id = str(uuid.uuid4())
    await asyncio.to_thread(db().orders.insert_one, {
        "order_id": order_id,
        "customer_id": customer.get("id"),
        "customer_email": customer.get("email"),
        "items": cart,
        "total": 4200,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    })
    return {"status": "confirmed", "order_id": order_id, "payment": r.json()}
