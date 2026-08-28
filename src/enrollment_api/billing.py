"""Payroll deduction codes for priced elections.

Finance requires a stable deduction code per rate table so that a member's
payroll deduction can be reconciled to the premium that produced it. The map
below is maintained here, in this service, because the codes come from the
payroll vendor rather than from the plan catalog.

Every rate table published by northwind-plan-config that this service prices
against must have an entry. A rate table that is retired or repointed upstream
without a matching entry here stops the payroll file dead.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Iterable, List

from enrollment_api.models.plan_summary import Election

LOGGER = logging.getLogger(__name__)

PAYROLL_DEDUCTION_CODES: Dict[str, str] = {
    "ACC-2200-2027A": "ACC27",
    "CI-3000-2027A": "CRIT27",
    "HI-1500-2027A": "HOSP27",
    "DEN-1000-2026A": "DENT26",
}


class UnmappedRateTable(Exception):
    """Raised when a priced election points at a rate table finance cannot code."""


def deduction_code_for(rate_table_id: str) -> str:
    """The payroll deduction code for a rate table."""
    code = PAYROLL_DEDUCTION_CODES.get(rate_table_id)
    if code is None:
        raise UnmappedRateTable(
            "rate table {} has no payroll deduction code; the payroll vendor "
            "will reject the whole deduction file".format(rate_table_id)
        )
    return code


def deduction_rows(elections: Iterable[Election], member_id: str) -> List[Dict[str, Any]]:
    """Payroll deduction rows for one member's elections."""
    rows = []
    for election in elections:
        election.deduction_code = deduction_code_for(election.plan.rate_table_id)
        rows.append(
            {
                "member_id": member_id,
                "plan_id": election.plan.plan_id,
                "deduction_code": election.deduction_code,
                "monthly_amount": election.monthly_premium,
                "effective_date": election.plan.effective_date,
            }
        )
    return rows


def total_monthly_deduction(elections: Iterable[Election]) -> Decimal:
    """What the member sees deducted each month across all elections."""
    total = Decimal("0.00")
    for election in elections:
        total += election.monthly_premium
    return total
