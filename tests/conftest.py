import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from enrollment_api.models.plan_summary import PlanSummary  # noqa: E402


def plan_payload(plan_id, state, rate_table_id, gi_amount, form_number, product_line):
    """A plan summary shaped exactly as GET /plans on the catalog returns it."""
    return {
        "plan_id": plan_id,
        "plan_name": "{} plan".format(plan_id),
        "product_line": product_line,
        "carrier_id": "NW-LIFE",
        "plan_year": 2027,
        "effective_date": "2027-01-01",
        "state": state,
        "rate_table_id": rate_table_id,
        "guaranteed_issue_amount": gi_amount,
        "form_number": form_number,
        "riders": [],
        "billing_modes": ["payroll_deduct"],
        "priced_states": ["AL", "FL", "GA", "TN", "TX"],
    }


@pytest.fixture
def critical_illness_tx():
    return PlanSummary(
        plan_payload("CI-3000", "TX", "CI-3000-2027A", 30000, "C3000-TX-R1", "critical_illness")
    )


@pytest.fixture
def dental_tx():
    # The dental plan is still priced from the 2026 rate table.
    return PlanSummary(
        plan_payload("DEN-1000", "TX", "DEN-1000-2026A", 1000, "D1000-TX-R1", "dental")
    )


@pytest.fixture
def rate_tables():
    return {
        "CI-3000-2027A": {
            "rate_table_id": "CI-3000-2027A",
            "rate_basis": "per_1000_of_benefit_monthly",
            "rates_by_state": {
                "TX": {"18-29": 0.6448, "40-49": 1.6016},
                "GA": {"18-29": 0.62, "40-49": 1.54},
            },
        },
        "DEN-1000-2026A": {
            "rate_table_id": "DEN-1000-2026A",
            "rate_basis": "flat_monthly_per_member",
            "rates_by_state": {
                "TX": {"18-29": 29.536, "40-49": 34.112},
                "GA": {"18-29": 28.40, "40-49": 32.80},
            },
        },
    }


class FakeCatalog(object):
    """Stands in for the plan catalog service in tests."""

    def __init__(self, rate_tables):
        self._rate_tables = rate_tables
        self.requested = []

    def rate_table(self, rate_table_id):
        self.requested.append(rate_table_id)
        if rate_table_id not in self._rate_tables:
            raise KeyError("catalog returned 404 for {}".format(rate_table_id))
        return self._rate_tables[rate_table_id]


@pytest.fixture
def catalog(rate_tables):
    return FakeCatalog(rate_tables)
