"""The storefront's back office, faked in memory so the lab has no database.

get_shipping_eta fails about one call in four, on purpose: a failing tool is
the span you most want to see, and the one nobody emits for you.
"""

import os
import random
import time

from strands import tool

ORDERS = {
    "1042": {"status": "shipped", "items": ["blue ceramic mug", "espresso cups x2"], "carrier": "DHL"},
    "1043": {"status": "processing", "items": ["walnut cutting board"], "carrier": None},
    "1044": {"status": "delivered", "items": ["linen apron", "blue ceramic mug"], "carrier": "An Post"},
    "1045": {"status": "cancelled", "items": ["cast iron skillet"], "carrier": None},
}

INVENTORY = {
    "blue ceramic mug": 12,
    "espresso cups": 0,
    "walnut cutting board": 3,
    "linen apron": 27,
    "cast iron skillet": 5,
    "french press": 0,
}

FAILURE_RATE = float(os.environ.get("SHIPPING_FAILURE_RATE", "0.25"))


@tool
def lookup_order(order_id: str) -> dict:
    """Look up an order by its number and return its status, items and carrier."""
    time.sleep(random.uniform(0.05, 0.2))
    order = ORDERS.get(order_id.strip().lstrip("#"))
    if order is None:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order_id": order_id, **order}


@tool
def check_inventory(product: str) -> dict:
    """Return how many units of a product are in stock."""
    time.sleep(random.uniform(0.05, 0.15))
    name = product.strip().lower()
    for known, units in INVENTORY.items():
        if name in known or known in name:
            return {"product": known, "in_stock": units}
    return {"product": product, "in_stock": None, "note": "not a product we sell"}


# #region flaky
@tool
def get_shipping_eta(order_id: str) -> dict:
    """Ask the carrier's API when a shipped order will arrive."""
    time.sleep(random.uniform(0.3, 1.2))
    if random.random() < FAILURE_RATE:
        raise TimeoutError("carrier API did not answer within 1s (upstream timeout)")
    order = ORDERS.get(order_id.strip().lstrip("#"))
    if not order or order["status"] != "shipped":
        return {"order_id": order_id, "eta": None, "reason": "order is not in transit"}
    return {"order_id": order_id, "carrier": order["carrier"], "eta_days": random.randint(1, 4)}
# #endregion flaky


STEP_2_TOOLS = [lookup_order, check_inventory, get_shipping_eta]
