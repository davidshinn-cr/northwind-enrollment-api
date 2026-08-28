from decimal import Decimal

from enrollment_api import quoting
from enrollment_api.models.plan_summary import Election


def test_per_1000_election_is_priced_from_the_state_row(critical_illness_tx, rate_tables):
    premium = quoting.monthly_premium(
        critical_illness_tx, rate_tables["CI-3000-2027A"], 20000, "40-49"
    )
    assert premium == Decimal("32.00")


def test_flat_plan_is_priced_at_the_state_row(dental_tx, rate_tables):
    premium = quoting.monthly_premium(
        dental_tx, rate_tables["DEN-1000-2026A"], 1000, "40-49"
    )
    assert premium == Decimal("34.11")


def test_pricing_an_election_fetches_and_caches_the_rate_table(
    critical_illness_tx, catalog
):
    cache = {}
    first = quoting.price_election(Election(critical_illness_tx, 20000, "40-49"), catalog, cache)
    second = quoting.price_election(Election(critical_illness_tx, 20000, "40-49"), catalog, cache)

    assert first.monthly_premium == second.monthly_premium == Decimal("32.00")
    assert catalog.requested == ["CI-3000-2027A"]


def test_a_state_with_no_rate_rows_prices_at_zero(critical_illness_tx, rate_tables):
    # Documented behaviour: enrolment continues rather than failing.
    table = rate_tables["CI-3000-2027A"]
    assert quoting.rate_for(table, "WY", "40-49") == Decimal("0.00")
