"""A stand-in for the external payment service provider."""

import asyncio
import random

from fastapi import FastAPI

app = FastAPI()


@app.post("/authorize")
async def authorize(req: dict) -> dict:
    await asyncio.sleep(random.uniform(0.06, 0.1))
    return {"authorized": True, "ref": req.get("merchant_ref")}
