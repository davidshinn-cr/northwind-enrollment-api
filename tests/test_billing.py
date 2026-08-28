import pytest

from enrollment_api import billing
from enrollment_api.models.plan_summary import Election


def test_every_rate_table_the_service_prices_has_a_deduction_code(
    critical_illness_tx, dental_tx
):
    for plan in (critical_illness_tx, dental_tx):
        assert billing.deduction_code_for(plan.rate_table_id)


def test_an_unmapped_rate_table_stops_the_payroll_file():
    with pytest.raises(billing.UnmappedRateTable):
        billing.deduction_code_for("DEN-1000-2027A")


def test_deduction_rows_carry_the_finance_code(dental_tx):
    election = Election(dental_tx, 1000, "40-49")
    rows = billing.deduction_rows([election], "M-100294")
    assert rows[0]["deduction_code"] == "DENT26"
