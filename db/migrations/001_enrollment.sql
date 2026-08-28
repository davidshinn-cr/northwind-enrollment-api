-- 001_enrollment.sql
-- Enrolment records written by the member-facing enrolment experience.
--
-- plan_id, situs_state, form_number and deduction_code all originate in
-- northwind-plan-config. They are denormalised onto the row because an
-- enrolment is a contract: it records what the member was actually sold, at the
-- price they were actually shown, even after the catalog moves on.

CREATE TABLE IF NOT EXISTS enrollment (
    enrollment_id    BIGSERIAL PRIMARY KEY,
    member_id        TEXT          NOT NULL,
    group_id         TEXT          NOT NULL,
    plan_id          TEXT          NOT NULL,
    situs_state      CHAR(2)       NOT NULL,
    form_number      TEXT          NOT NULL,
    benefit_amount   INTEGER       NOT NULL CHECK (benefit_amount >= 0),
    age_band         TEXT          NOT NULL,
    monthly_premium  NUMERIC(10,2) NOT NULL CHECK (monthly_premium >= 0),
    deduction_code   TEXT          NOT NULL,
    effective_date   DATE          NOT NULL,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_enrollment_member ON enrollment (member_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_group_plan ON enrollment (group_id, plan_id);

-- A premium of zero is legal for an employer-paid plan, so nothing here
-- rejects it. Reporting watches for it instead.
CREATE OR REPLACE VIEW v_zero_premium_enrollments AS
SELECT
    e.group_id,
    e.plan_id,
    e.situs_state,
    COUNT(*) AS enrollment_count
FROM enrollment AS e
WHERE e.monthly_premium = 0
GROUP BY e.group_id, e.plan_id, e.situs_state;
