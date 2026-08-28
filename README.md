# northwind-enrollment-api

The member-facing enrolment experience for the Northwind voluntary benefits
platform.

Northwind is a synthetic reference codebase. This service is the downstream
consumer in a two-service pair: the plan data lives in
[`northwind-plan-config`](https://github.com/davidshinn-cr/northwind-plan-config)
and reaches members through here.

```
northwind-plan-config              northwind-enrollment-api
─────────────────────              ────────────────────────
config/plans/*.json
        │
     seed ──► plan_state
        │
  catalog_api  GET /plans ─────►  plan_catalog_client
                                          │
                                    build_offer_set  ──►  what the member sees
                                          │
  GET /rate-tables/{id} ────────►      quoting  ──────►  the premium shown
                                          │
                                      billing  ──────►  payroll deduction file
                                          │
                                       enroll  ──────►  enrollment
```

## What is in here

| Path | What |
| --- | --- |
| `src/enrollment_api/clients/` | HTTP client for the plan catalog |
| `src/enrollment_api/models/` | This service's hand-maintained copy of the catalog contract |
| `src/enrollment_api/offers.py` | The member's offer set |
| `src/enrollment_api/quoting.py` | Pricing an election against a published rate table |
| `src/enrollment_api/billing.py` | Payroll deduction codes, keyed by rate table identifier |
| `src/enrollment_api/enroll.py` | Validating and writing the enrolment record |
| `db/migrations/` | The enrolment table and the zero-premium reporting view |

`AGENTS.md` describes what this service consumes from the catalog and, more
usefully, where an upstream change lands when it goes wrong.

## Running the tests

```bash
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```
