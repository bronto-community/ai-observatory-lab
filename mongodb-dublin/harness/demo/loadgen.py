"""Steady shop traffic: browsing and checkouts from returning and new customers."""

import asyncio
import os
import random

import httpx

WEB = os.environ.get("WEB_URL", "http://web:8000")
CHECKOUT_RPS = float(os.environ.get("CHECKOUT_RPS", "2"))
BROWSE_RPS = float(os.environ.get("BROWSE_RPS", "6"))
CUSTOMERS = int(os.environ.get("SEED_CUSTOMERS", "50000"))


async def every(rps: float, fn, client) -> None:
    while True:
        asyncio.create_task(fn(client))
        await asyncio.sleep(random.expovariate(rps))


async def browse(client) -> None:
    try:
        await client.get(f"{WEB}/browse")
    except httpx.HTTPError:
        pass


async def checkout(client) -> None:
    n = random.randint(1, CUSTOMERS * 2)  # half of them are new
    customer = {"id": f"c{n}", "email": f"customer{n}@example.com"}
    cart = random.sample([f"sku-{i}" for i in range(1, 41)], k=random.randint(1, 3))
    try:
        await client.post(f"{WEB}/checkout", json={"customer": customer, "cart": cart})
    except httpx.HTTPError:
        pass


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        await asyncio.gather(every(CHECKOUT_RPS, checkout, client), every(BROWSE_RPS, browse, client))


asyncio.run(main())
