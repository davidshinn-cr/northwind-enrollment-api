"""The catalog contract, as this service consumes it.

These classes mirror the payload returned by ``GET /plans`` on
northwind-plan-config. They are maintained here by hand: the catalog is a
separate service in a separate repository, so a field renamed, removed or
re-typed there is not a compile error here. It is a runtime KeyError, or worse,
a silently missing value on a member's screen.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

CONTRACT_VERSION = "2027.1.0"

# Fields this service requires from every plan summary the catalog returns.
REQUIRED_PLAN_SUMMARY_FIELDS = (
    "plan_id",
    "plan_name",
    "product_line",
    "carrier_id",
    "plan_year",
    "effective_date",
    "state",
    "rate_table_id",
    "guaranteed_issue_amount",
    "form_number",
    "riders",
    "billing_modes",
)


class ContractMismatch(Exception):
    """Raised when the catalog returns a payload this service cannot read."""


class PlanSummary(object):
    """One plan as the member's offer set sees it."""

    def __init__(self, payload: Dict[str, Any]):
        missing = [f for f in REQUIRED_PLAN_SUMMARY_FIELDS if f not in payload]
        if missing:
            raise ContractMismatch(
                "plan catalog response is missing {}; this service expects "
                "contract {}".format(", ".join(missing), CONTRACT_VERSION)
            )

        self.plan_id: str = payload["plan_id"]
        self.plan_name: str = payload["plan_name"]
        self.product_line: str = payload["product_line"]
        self.carrier_id: str = payload["carrier_id"]
        self.plan_year: int = payload["plan_year"]
        self.effective_date: str = payload["effective_date"]
        self.state: str = payload["state"]
        self.rate_table_id: str = payload["rate_table_id"]
        self.guaranteed_issue_amount: Optional[int] = payload["guaranteed_issue_amount"]
        self.form_number: Optional[str] = payload["form_number"]
        self.riders: List[str] = payload["riders"]
        self.billing_modes: List[str] = payload["billing_modes"]

    def __repr__(self):
        return "PlanSummary({} in {})".format(self.plan_id, self.state)


class Election(object):
    """One member's election of one plan."""

    def __init__(self, plan: PlanSummary, benefit_amount: int, age_band: str):
        self.plan = plan
        self.benefit_amount = benefit_amount
        self.age_band = age_band
        self.monthly_premium: Decimal = Decimal("0.00")
        self.deduction_code: Optional[str] = None
