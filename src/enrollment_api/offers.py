"""Build the set of plans a member is shown during open enrolment."""

import logging
from typing import Any, Dict, List, Optional

from enrollment_api.models.plan_summary import PlanSummary

LOGGER = logging.getLogger(__name__)


class Offer(object):
    """One plan as presented to a member, with the elections they may make."""

    def __init__(self, plan: PlanSummary, max_election_without_underwriting: Optional[int]):
        self.plan = plan
        self.max_election_without_underwriting = max_election_without_underwriting

    def as_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan.plan_id,
            "plan_name": self.plan.plan_name,
            "product_line": self.plan.product_line,
            "state": self.plan.state,
            "effective_date": self.plan.effective_date,
            "rate_table_id": self.plan.rate_table_id,
            "max_election_without_underwriting": self.max_election_without_underwriting,
            "riders": self.plan.riders,
        }


def build_offer_set(plans: List[PlanSummary]) -> List[Offer]:
    """Turn the catalog response into the member's offer set.

    Presentation is deliberately forgiving: a plan the catalog published is a
    plan the member is shown. A plan with no guaranteed issue amount for the
    member's state is still offered, with the underwriting ceiling left blank.
    """
    offers = []
    for plan in plans:
        if plan.guaranteed_issue_amount is None:
            LOGGER.warning(
                "plan %s is published in %s with no guaranteed issue amount; "
                "offering it with no underwriting ceiling",
                plan.plan_id,
                plan.state,
            )
        offers.append(Offer(plan, plan.guaranteed_issue_amount))
    return offers


def offer_for(offers: List[Offer], plan_id: str) -> Optional[Offer]:
    """Find one offer in a member's offer set."""
    for offer in offers:
        if offer.plan.plan_id == plan_id:
            return offer
    return None
