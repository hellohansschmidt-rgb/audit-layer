"""
Generates synthetic OpenTelemetry-style spans representing AI agent calls,
for use as test fixtures in test_telemetry_compliance.py.

Schema deliberately mirrors real OTel span shape (trace_id, span_id,
attributes dict) so it reads as credible telemetry rather than a toy format.
Swap in your actual fixture org names/tiers below to match your existing
governance-critic-evals fixtures.
"""

import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- Replace these with your actual fixture org identifiers ---
FIXTURE_ORGS = [
    {"org_id": "org_conservative_industrial", "latency_sla_ms": 3000},
    {"org_id": "org_regulated_finance", "latency_sla_ms": 2000},
    {"org_id": "org_startup_fast_iteration", "latency_sla_ms": 5000},
]

AGENT_IDS = ["contract-reviewer-v1", "compliance-auditor-v1", "manual-rag-v1"]

BIAS_TERM_POOL = ["gender-coded-phrase", "age-coded-phrase", "protected-class-reference"]


def make_span(org_id: str, latency_sla_ms: int, force_violation: bool = False) -> dict:
    """Build a single synthetic span. force_violation lets you guarantee
    at least one failing case per org, so the pytest suite has something
    real to catch (a clean-only fixture set proves nothing)."""

    trace_id = uuid.uuid4().hex
    span_id = uuid.uuid4().hex[:16]
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 4320))

    output_contains_pii = force_violation and random.random() < 0.5
    latency_ms = (
        latency_sla_ms + random.randint(200, 1500)
        if force_violation and not output_contains_pii
        else random.randint(300, latency_sla_ms - 200)
    )
    model_confidence = (
        round(random.uniform(0.40, 0.62), 2)
        if force_violation and not output_contains_pii and latency_ms <= latency_sla_ms
        else round(random.uniform(0.75, 0.99), 2)
    )
    flagged_bias_terms = (
        [random.choice(BIAS_TERM_POOL)]
        if random.random() < 0.08
        else []
    )
    # A flagged term is only a real gap if no reviewer signed off on it
    bias_review_status = "reviewed" if flagged_bias_terms and random.random() < 0.5 else None

    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "name": "agent.invoke",
        "timestamp": timestamp.isoformat(),
        "attributes": {
            "org_id": org_id,
            "agent_id": random.choice(AGENT_IDS),
            "input_contains_pii": random.random() < 0.15,
            "output_contains_pii": output_contains_pii,
            "latency_ms": latency_ms,
            "latency_sla_ms": latency_sla_ms,
            "model_confidence": model_confidence,
            "flagged_bias_terms": flagged_bias_terms,
            "bias_review_status": bias_review_status,
        },
    }


def generate_org_spans(org: dict, n_clean: int = 12, n_violations: int = 3) -> list[dict]:
    spans = [make_span(org["org_id"], org["latency_sla_ms"]) for _ in range(n_clean)]
    spans += [
        make_span(org["org_id"], org["latency_sla_ms"], force_violation=True)
        for _ in range(n_violations)
    ]
    random.shuffle(spans)
    return spans


def main():
    out_dir = Path(__file__).parent
    for org in FIXTURE_ORGS:
        spans = generate_org_spans(org)
        out_path = out_dir / f"sample_spans_{org['org_id']}.json"
        out_path.write_text(json.dumps(spans, indent=2))
        print(f"wrote {len(spans)} spans -> {out_path}")


if __name__ == "__main__":
    main()
