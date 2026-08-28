"""Northwind enrolment experience.

The member-facing service. It reads the published plan catalog from
``northwind-plan-config``, builds the offer set a member is shown, prices their
elections, and writes the enrolment record.

This service owns none of the plan data. Everything it shows a member is
derived from the catalog contract.
"""

__version__ = "2027.1.0"
