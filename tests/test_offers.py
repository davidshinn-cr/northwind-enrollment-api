from enrollment_api.models.plan_summary import ContractMismatch, PlanSummary
from enrollment_api.offers import build_offer_set, offer_for

import pytest


def test_offer_set_carries_the_underwriting_ceiling(critical_illness_tx):
    offers = build_offer_set([critical_illness_tx])
    assert offers[0].max_election_without_underwriting == 30000


def test_a_plan_with_no_filed_ceiling_is_still_offered(critical_illness_tx):
    critical_illness_tx.guaranteed_issue_amount = None
    offers = build_offer_set([critical_illness_tx])
    assert offers[0].max_election_without_underwriting is None


def test_offer_lookup_by_plan_id(critical_illness_tx, dental_tx):
    offers = build_offer_set([critical_illness_tx, dental_tx])
    assert offer_for(offers, "DEN-1000").plan.plan_id == "DEN-1000"
    assert offer_for(offers, "HI-1500") is None


def test_a_catalog_payload_missing_a_contract_field_is_rejected():
    with pytest.raises(ContractMismatch):
        PlanSummary({"plan_id": "CI-3000"})
