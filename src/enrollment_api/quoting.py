"""Price a member's elections against the published rate tables.

Rates are owned by northwind-plan-config. This service fetches the table a plan
points at and reads the member's state and age band out of it.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from enrollment_api.models.plan_summary import Election, PlanSummary

LOGGER = logging.getLogger(__name__)

CENTS = Decimal("0.01")
ZERO = Decimal("0.00")


def rate_for(rate_table: Dict[str, Any], state: str, age_band: str) -> Decimal:
    """The published rate for a state and age band.

    Enrolment must not fail because a rate row is missing, so an absent state
    or age band prices at zero and the member is allowed to continue.
    """
    state_rates = rate_table.get("rates_by_state", {}).get(state)
    if state_rates is None:
        LOGGER.warning(
            "rate table %s has no rows for state %s; pricing at zero",
            rate_table.get("rate_table_id"),
            state,
        )
        return ZERO

    raw = state_rates.get(age_band)
    if raw is None:
        LOGGER.warning(
            "rate table %s has no %s row for state %s; pricing at zero",
            rate_table.get("rate_table_id"),
            age_band,
            state,
        )
        return ZERO

    return Decimal(str(raw)).quantize(CENTS)


def monthly_premium(
    plan: PlanSummary,
    rate_table: Dict[str, Any],
    benefit_amount: int,
    age_band: str,
) -> Decimal:
    """Monthly premium for one election."""
    rate = rate_for(rate_table, plan.state, age_band)

    if rate_table.get("rate_basis") == "per_1000_of_benefit_monthly":
        units = Decimal(benefit_amount) / Decimal("1000")
        return (rate * units).quantize(CENTS)

    return rate.quantize(CENTS)


def price_election(
    election: Election,
    catalog: Any,
    rate_table_cache: Optional[Dict[str, Any]] = None,
) -> Election:
    """Resolve the rate table for an election and set its monthly premium."""
    cache = rate_table_cache if rate_table_cache is not None else {}
    rate_table_id = election.plan.rate_table_id

    if rate_table_id not in cache:
        cache[rate_table_id] = catalog.rate_table(rate_table_id)

    election.monthly_premium = monthly_premium(
        election.plan, cache[rate_table_id], election.benefit_amount, election.age_band
    )
    return election
