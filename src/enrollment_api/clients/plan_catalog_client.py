"""HTTP client for the plan catalog published by northwind-plan-config."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from enrollment_api import settings
from enrollment_api.models.plan_summary import PlanSummary

LOGGER = logging.getLogger(__name__)


class PlanCatalogUnavailable(Exception):
    """Raised when the catalog cannot be reached or returns an error."""


class PlanCatalogClient(object):
    """Read-only client for ``GET /plans`` and ``GET /rate-tables/{id}``."""

    def __init__(self, base_url: Optional[str] = None, client: Optional[Any] = None):
        self.base_url = (base_url or settings.PLAN_CATALOG_BASE_URL).rstrip("/")
        self._client = client or httpx.Client(timeout=settings.PLAN_CATALOG_TIMEOUT_SECONDS)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = "{}{}".format(self.base_url, path)
        try:
            response = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise PlanCatalogUnavailable("{} failed: {}".format(url, exc))
        if response.status_code >= 400:
            raise PlanCatalogUnavailable(
                "{} returned {}".format(url, response.status_code)
            )
        return response.json()

    def list_plans(
        self,
        group_id: str,
        member_state: str,
        channel: str = settings.DEFAULT_CHANNEL,
        as_of: Optional[str] = None,
    ) -> List[PlanSummary]:
        """Every plan the catalog says this member may be offered."""
        params = {"group_id": group_id, "member_state": member_state, "channel": channel}
        if as_of:
            params["as_of"] = as_of
        payload = self._get("/plans", params)
        return [PlanSummary(item) for item in payload["plans"]]

    def rate_table(self, rate_table_id: str) -> Dict[str, Any]:
        """The published rate table behind a plan's ``rate_table_id``."""
        return self._get("/rate-tables/{}".format(rate_table_id))
