"""Runtime configuration for the enrolment service."""

import os

# The plan catalog published by northwind-plan-config.
PLAN_CATALOG_BASE_URL = os.environ.get(
    "PLAN_CATALOG_BASE_URL", "http://plan-catalog.internal:8000"
)

PLAN_CATALOG_TIMEOUT_SECONDS = float(os.environ.get("PLAN_CATALOG_TIMEOUT_SECONDS", "3.0"))

# Rate tables are fetched once per open-enrolment window and held for the
# duration, because they do not change inside a plan year.
RATE_TABLE_CACHE_TTL_SECONDS = int(os.environ.get("RATE_TABLE_CACHE_TTL_SECONDS", "86400"))

DEFAULT_CHANNEL = "worksite"
