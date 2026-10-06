"""storefront-web -- the customer-facing entry point."""

import logging
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from services.common import telemetry

app = FastAPI(title="storefront-web")
telemetry.setup(app)
log = logging.getLogger("storefront-web")

CHECKOUT_URL = os.environ.get("CHECKOUT_URL", "http://checkout:8000")
CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog:8000")

client = httpx.AsyncClient(timeout=5.0)


@app.on_event("startup")
async def startup() -> None:
    telemetry.announce_release()


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}


@app.get("/browse")
async def browse() -> dict:
    r = await client.get(f"{CATALOG_URL}/items")
    return {"items": r.json()["items"]}


@app.post("/checkout")
async def checkout(req: dict | None = None) -> dict:
    req = req or {}
    body = {"cart": req.get("cart", ["sku-1"]), "customer": req.get("customer", {})}
    try:
        r = await client.post(f"{CHECKOUT_URL}/checkout", json=body)
        r.raise_for_status()
    except httpx.HTTPError as e:
        log.error("checkout failed: %s", e)
        raise HTTPException(status_code=503, detail="checkout unavailable") from e
    return r.json()


# The shop itself: the page and product images. Mounted last so the API routes win.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="shop")
