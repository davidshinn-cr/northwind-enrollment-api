"""The member-facing enrolment API."""

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query

from enrollment_api import settings
from enrollment_api.clients.plan_catalog_client import (
    PlanCatalogClient,
    PlanCatalogUnavailable,
)
from enrollment_api.models.plan_summary import ContractMismatch
from enrollment_api.offers import build_offer_set

app = FastAPI(title="Northwind Enrolment", version="2027.1.0")

_catalog = PlanCatalogClient()


@app.get("/enrollment/offers")
def offers(
    member_id: str = Query(...),
    group_id: str = Query(...),
    member_state: str = Query(..., min_length=2, max_length=2),
    channel: str = Query(settings.DEFAULT_CHANNEL),
    as_of: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Everything this member may elect during open enrolment."""
    try:
        plans = _catalog.list_plans(group_id, member_state, channel, as_of)
    except PlanCatalogUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ContractMismatch as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    offer_set: List[Any] = build_offer_set(plans)
    return {
        "member_id": member_id,
        "group_id": group_id,
        "member_state": member_state,
        "offers": [offer.as_dict() for offer in offer_set],
    }
