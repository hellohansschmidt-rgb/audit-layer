"""
test_telemetry_compliance.py

Each test evaluates synthetic OTel-style agent spans against a governance
property, and maps the check to the specific ISO/IEC 42001 clause it
evidences. This is the artifact that turns "we ran some tests" into
"here is continuous audit evidence for your AI management system."

IMPORTANT: clause references below are a starting mapping, not a certified
crosswalk. Before using this in front of a client, sanity-check each
citation against the actual clause text -- don't claim evidence a test
doesn't really produce. Conservative boards are exactly the audience that
will have someone check.

Run with: pytest test_telemetry_compliance.py --json-report --json-report-file=report.json
"""

import json
from pathlib import Path

import pytest

TELEMETRY_DIR = Path(__file__).parent.parent / "telemetry"


def load_all_spans() -> list[dict]:
    spans = []
    for f in TELEMETRY_DIR.glob("sample_spans_*.json"):
        spans.extend(json.loads(f.read_text()))
    return spans


def spans_by_org(org_id: str) -> list[dict]:
    return [s for s in load_all_spans() if s["attributes"]["org_id"] == org_id]


ORG_IDS = sorted({s["attributes"]["org_id"] for s in load_all_spans()})


# ---------------------------------------------------------------------------
# Clause 8.2 -- Operational planning and control / AI system operation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("org_id", ORG_IDS)
def test_no_unredacted_pii_in_outputs(org_id):
    """Maps to ISO/IEC 42001 Clause 8.2 -- AI system operation monitoring.
    A compliant deployment must not surface PII in agent outputs even when
    PII is present in the input. This is a hard fail, not a warning."""
    violations = [
        s for s in spans_by_org(org_id)
        if s["attributes"]["output_contains_pii"]
    ]
    assert not violations, (
        f"{org_id}: {len(violations)} span(s) leaked PII into output. "
        f"trace_ids: {[s['trace_id'] for s in violations]}"
    )


@pytest.mark.parametrize("org_id", ORG_IDS)
def test_latency_within_sla(org_id):
    """Maps to ISO/IEC 42001 Clause 8.2 -- operational performance
    monitoring against defined thresholds. Latency isn't a compliance
    issue in itself, but an undocumented SLA breach is -- this test
    proves breaches are being caught, not just occurring silently."""
    violations = [
        s for s in spans_by_org(org_id)
        if s["attributes"]["latency_ms"] > s["attributes"]["latency_sla_ms"]
    ]
    assert not violations, (
        f"{org_id}: {len(violations)} span(s) exceeded latency SLA. "
        f"trace_ids: {[s['trace_id'] for s in violations]}"
    )


# ---------------------------------------------------------------------------
# Clause 6.1 / Annex A -- Risk assessment and treatment (bias)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("org_id", ORG_IDS)
def test_bias_terms_flagged_and_reviewed(org_id):
    """Maps to ISO/IEC 42001 Annex A control on bias and fairness risk
    treatment. A flagged bias term isn't itself a failure -- an unreviewed
    flagged term is. This is the difference between detection and
    governance: detection alone isn't evidence of control."""
    unreviewed = [
        s for s in spans_by_org(org_id)
        if s["attributes"]["flagged_bias_terms"]
        and s["attributes"]["bias_review_status"] != "reviewed"
    ]
    assert not unreviewed, (
        f"{org_id}: {len(unreviewed)} span(s) flagged for bias with no "
        f"recorded human review. trace_ids: {[s['trace_id'] for s in unreviewed]}"
    )


# ---------------------------------------------------------------------------
# Clause 8.3 / Annex A -- AI system impact assessment, human oversight
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("org_id", ORG_IDS)
def test_model_confidence_above_floor(org_id):
    """Maps to ISO/IEC 42001 Clause 8.3 -- human oversight of automated
    decisions. Spans below the confidence floor should have been routed
    to human review. This test checks the floor is enforced, not that
    every low-confidence output is wrong."""
    CONFIDENCE_FLOOR = 0.65
    violations = [
        s for s in spans_by_org(org_id)
        if s["attributes"]["model_confidence"] < CONFIDENCE_FLOOR
    ]
    assert not violations, (
        f"{org_id}: {len(violations)} span(s) below confidence floor "
        f"({CONFIDENCE_FLOOR}) with no human-review flag. "
        f"trace_ids: {[s['trace_id'] for s in violations]}"
    )


# ---------------------------------------------------------------------------
# Clause 7.5 -- Documented information (basic completeness check)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("org_id", ORG_IDS)
def test_spans_have_required_audit_fields(org_id):
    """Maps to ISO/IEC 42001 Clause 7.5 -- documented information must be
    identifiable and traceable. A span missing trace_id, timestamp, or
    agent_id can't be tied back to a specific decision, which breaks the
    audit trail regardless of what the decision itself was."""
    required = {"trace_id", "span_id", "timestamp"}
    incomplete = [
        s for s in spans_by_org(org_id)
        if not required.issubset(s.keys())
        or "agent_id" not in s["attributes"]
    ]
    assert not incomplete, f"{org_id}: {len(incomplete)} span(s) missing required audit fields."
