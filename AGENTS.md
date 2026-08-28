# Northwind Enrolment — service brief

The member-facing enrolment experience. During open enrolment this service
shows an employee the plans they may elect, prices those elections, and writes
the enrolment record and the payroll deduction rows.

**This service owns no plan data.** Everything a member sees is derived from the
plan catalog published by
[`northwind-plan-config`](https://github.com/davidshinn-cr/northwind-plan-config).

## What it consumes

| Upstream | What this service does with it |
| --- | --- |
| `GET /plans` | The member's offer set. Every field of the response is mirrored by hand in `models/plan_summary.py`. |
| `GET /rate-tables/{rate_table_id}` | The premium for an election, read by state and age band. |
| `rate_table_id` | The key into `billing.PAYROLL_DEDUCTION_CODES`, which finance maintains here. |
| `availability.states` (indirectly) | Whether a plan appears in the offer set at all. This service never sees the list; it sees the plans that survived it. |

## Where upstream changes land

The catalog is a separate service in a separate repository. Nothing in this
repository breaks at build time when it changes.

- **A contract field renamed, removed or re-typed** surfaces as a
  `ContractMismatch` from `models/plan_summary.py`, at run time, on a member's
  request — a 502 during open enrolment.
- **A rate table identifier retired or repointed** resolves to a 404 from the
  catalog, and, if it does resolve, to an `UnmappedRateTable` from `billing.py`
  because the payroll deduction code is keyed on the old identifier. The payroll
  vendor rejects the whole deduction file, not the one row.
- **A state published upstream with no rate rows** does not raise anywhere.
  `quoting.rate_for` returns zero and the member is shown a premium of $0.00,
  elects the plan, and is enrolled at that price. `v_zero_premium_enrollments`
  is the only place this shows up, after the fact.
- **A state published upstream with no guaranteed issue amount** does not raise
  either. `offers.build_offer_set` presents the plan with no underwriting
  ceiling, so an election that should have required medical underwriting is
  written straight through.

Both of those last two are deliberate: enrolment must not fail mid-session for a
data gap. The cost is that a data gap becomes a wrong answer rather than an
error, and only a review of the upstream change can catch it.

## Conventions

- `models/plan_summary.py` is the single place the catalog contract is written
  down. Nothing else should read raw catalog JSON.
- `billing.PAYROLL_DEDUCTION_CODES` must have an entry for every rate table this
  service prices against. Codes come from the payroll vendor, not the catalog.
- Enrolment rows are a record of what the member was sold. They denormalise the
  plan identifier, state, form number and premium on purpose, and are never
  back-filled when the catalog changes.
