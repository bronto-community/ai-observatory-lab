"""Runtime configuration for checkout-api."""

import os

# Outbound HTTP connection pool for the payments-gateway client.
PAYMENTS_POOL_SIZE = int(os.environ.get("PAYMENTS_POOL_SIZE", "20"))

PAYMENTS_URL = os.environ.get("PAYMENTS_URL", "http://payments:8000")
PAYMENTS_TIMEOUT_S = float(os.environ.get("PAYMENTS_TIMEOUT_S", "10"))
