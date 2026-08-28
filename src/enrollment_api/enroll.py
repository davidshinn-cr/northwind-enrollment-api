"""Write the enrolment record and the downstream payroll rows."""

import logging
from typing import Any, Dict, List, Optional

from enrollment_api import billing, quoting
from enrollment_api.models.plan_summary import Election
from enrollment_api.offers import Offer

LOGGER = logging.getLogger(__name__)

INSERT_ENROLLMENT = """
INSERT INTO enrollment (
    member_id, group_id, plan_id, situs_state, form_number,
    benefit_amount, age_band, monthly_premium, deduction_code, effective_date
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


class ElectionRejected(Exception):
    """Raised when an election cannot be written as an enrolment."""


def validate_election(offer: Offer, benefit_amount: int) -> None:
    """Check one election before it becomes an enrolment record."""
    plan = offer.plan

    if plan.form_number is None:
        raise ElectionRejected(
            "{} has no filed form number for {}; the certificate cannot be "
            "issued".format(plan.plan_id, plan.state)
        )

    ceiling = offer.max_election_without_underwriting
    if ceiling is not None and benefit_amount > ceiling:
        raise ElectionRejected(
            "elected {} exceeds the {} guaranteed issue amount of {}".format(
                benefit_amount, plan.state, ceiling
            )
        )


def enrol(
    cursor,
    member_id: str,
    group_id: str,
    offers: List[Offer],
    elections: List[Dict[str, Any]],
    catalog: Any,
    rate_table_cache: Optional[Dict[str, Any]] = None,
) -> List[Election]:
    """Price, validate and write a member's elections."""
    from enrollment_api.offers import offer_for

    priced: List[Election] = []

    for raw in elections:
        offer = offer_for(offers, raw["plan_id"])
        if offer is None:
            raise ElectionRejected(
                "{} is not in this member's offer set".format(raw["plan_id"])
            )

        validate_election(offer, raw["benefit_amount"])

        election = Election(offer.plan, raw["benefit_amount"], raw["age_band"])
        quoting.price_election(election, catalog, rate_table_cache)
        election.deduction_code = billing.deduction_code_for(offer.plan.rate_table_id)
        priced.append(election)

    for election in priced:
        plan = election.plan
        cursor.execute(
            INSERT_ENROLLMENT,
            (
                member_id,
                group_id,
                plan.plan_id,
                plan.state,
                plan.form_number,
                election.benefit_amount,
                election.age_band,
                election.monthly_premium,
                election.deduction_code,
                plan.effective_date,
            ),
        )

    LOGGER.info(
        "enrolled %s in %d plan(s) totalling %s per month",
        member_id,
        len(priced),
        billing.total_monthly_deduction(priced),
    )
    return priced
