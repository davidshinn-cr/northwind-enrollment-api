import pytest

from enrollment_api import enroll
from enrollment_api.offers import build_offer_set


class FakeCursor(object):
    def __init__(self):
        self.rows = []

    def execute(self, sql, params):
        self.rows.append(params)


def test_enrolment_writes_a_priced_row(critical_illness_tx, catalog):
    cursor = FakeCursor()
    offers = build_offer_set([critical_illness_tx])

    enroll.enrol(
        cursor,
        "M-100294",
        "NW-GRP-0088",
        offers,
        [{"plan_id": "CI-3000", "benefit_amount": 20000, "age_band": "40-49"}],
        catalog,
    )

    assert len(cursor.rows) == 1
    assert cursor.rows[0][2] == "CI-3000"
    assert cursor.rows[0][4] == "C3000-TX-R1"


def test_an_election_above_the_ceiling_is_rejected(critical_illness_tx, catalog):
    offers = build_offer_set([critical_illness_tx])
    with pytest.raises(enroll.ElectionRejected):
        enroll.enrol(
            FakeCursor(),
            "M-100294",
            "NW-GRP-0088",
            offers,
            [{"plan_id": "CI-3000", "benefit_amount": 50000, "age_band": "40-49"}],
            catalog,
        )


def test_a_plan_with_no_filed_form_number_cannot_be_enrolled(critical_illness_tx, catalog):
    critical_illness_tx.form_number = None
    offers = build_offer_set([critical_illness_tx])
    with pytest.raises(enroll.ElectionRejected):
        enroll.enrol(
            FakeCursor(),
            "M-100294",
            "NW-GRP-0088",
            offers,
            [{"plan_id": "CI-3000", "benefit_amount": 10000, "age_band": "40-49"}],
            catalog,
        )
