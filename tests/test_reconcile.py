"""
test_reconcile.py

Pins the reconciliation truth table in generate_audit_report.reconcile()
-- the single deterministic decision function the whole engine depends on,
per reconciliation_mapping_spec.md ("This is the whole decision. No LLM
in the path.").
"""

import pytest

from generate_audit_report import reconcile


@pytest.mark.parametrize("declared, test_outcome, expected", [
    (True, "passed", "CONFIRMED"),
    (True, "failed", "CONTRADICTED"),
    (False, "passed", "UNDERSTATED"),
    (False, "failed", "CONSISTENT_GAP"),
    (None, "passed", "NOT_OBSERVABLE"),
    (None, "failed", "NOT_OBSERVABLE"),
    (True, None, "NOT_OBSERVABLE"),
    (False, None, "NOT_OBSERVABLE"),
    (None, None, "NOT_OBSERVABLE"),
    (True, "error", "NOT_OBSERVABLE"),
    (True, "skipped", "NOT_OBSERVABLE"),
    (False, "error", "NOT_OBSERVABLE"),
    (False, "skipped", "NOT_OBSERVABLE"),
])
def test_reconcile(declared, test_outcome, expected):
    assert reconcile(declared, test_outcome) == expected
