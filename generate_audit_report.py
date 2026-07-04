"""
generate_audit_report.py

Runs the compliance test suite, parses the JSON report, and produces a
one-page-per-org markdown summary mapping pass/fail to ISO 42001 clauses.
This is the artifact a board actually reads -- nobody reviews raw pytest
output.

Usage:
    pip install pytest-json-report --break-system-packages
    python3 generate_audit_report.py

Requires tests/test_telemetry_compliance.py to have been run with
--json-report first, or run it directly here.
"""

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
REPORT_JSON = ROOT / "pytest_report.json"

# Reuse the test suite's own span loader rather than re-parsing telemetry/
# separately -- one source of truth for "what a span is".
sys.path.insert(0, str(ROOT / "tests"))
from test_telemetry_compliance import spans_by_org as _spans_by_org  # noqa: E402

# control_id -> fn(spans) -> list[str]. Each extractor mirrors the exact
# violation predicate used by the corresponding pytest test, so the
# footnote is read off the span data, never synthesised.
EVIDENCE_EXTRACTORS = {
    "ctrl_01": lambda spans: [
        f"span `{s['span_id']}` (trace `{s['trace_id']}`): `output_contains_pii=True`"
        for s in spans if s["attributes"]["output_contains_pii"]
    ],
    "ctrl_02": lambda spans: [
        f"span `{s['span_id']}` (trace `{s['trace_id']}`): "
        f"latency_ms={s['attributes']['latency_ms']} > "
        f"latency_sla_ms={s['attributes']['latency_sla_ms']} "
        f"(Δ+{s['attributes']['latency_ms'] - s['attributes']['latency_sla_ms']}ms)"
        for s in spans if s["attributes"]["latency_ms"] > s["attributes"]["latency_sla_ms"]
    ],
}


def evidence_for(control_id: str, org: str) -> list[str]:
    """Deterministic span-level evidence for a CONTRADICTED control.
    Empty list if no extractor is registered for this control_id."""
    extractor = EVIDENCE_EXTRACTORS.get(control_id)
    if not extractor:
        return []
    return extractor(_spans_by_org(org))

# test function name -> control metadata. control_id/claim_text are the
# self-assessment side of the mapping in reconciliation_mapping_spec.md;
# control/clause are the existing short label used in the compliance table.
CLAUSE_MAP = {
    "test_no_unredacted_pii_in_outputs": {
        "control_id": "ctrl_01",
        "control": "Agent outputs do not leak PII",
        "claim_text": (
            "Agent outputs are screened so personal data is not exposed, "
            "even when it appears in the input."),
        "clause": "Clause 8.2",
    },
    "test_latency_within_sla": {
        "control_id": "ctrl_02",
        "control": "Operational performance within defined SLA",
        "claim_text": (
            "AI systems have defined performance thresholds, and breaches "
            "are detected rather than passing silently."),
        "clause": "Clause 8.2",
    },
    "test_bias_terms_flagged_and_reviewed": {
        "control_id": "ctrl_03",
        "control": "Flagged bias risks have recorded human review",
        "claim_text": (
            "Bias or fairness risks flagged by the system receive recorded "
            "human review."),
        "clause": "Annex A (risk treatment)",
    },
    "test_model_confidence_above_floor": {
        "control_id": "ctrl_04",
        "control": "Low-confidence outputs subject to human oversight",
        "claim_text": (
            "Low-confidence AI outputs are routed to human oversight."),
        "clause": "Clause 8.3",
    },
    "test_spans_have_required_audit_fields": {
        "control_id": "ctrl_05",
        "control": "Audit trail completeness / traceability",
        "claim_text": (
            "Every AI decision is traceable to an identifiable record."),
        "clause": "Clause 7.5",
    },
}

# Declaration-only controls -- no telemetry counterpart exists or ever will
# (see "Not observable in telemetry" in reconciliation_mapping_spec.md).
# These always resolve to NOT_OBSERVABLE regardless of the declared answer.
DECLARATION_ONLY_CONTROLS = [
    {
        "control_id": "ctrl_06",
        "claim_text": "A named, accountable AI governance owner exists.",
    },
    {
        "control_id": "ctrl_07",
        "claim_text": "An approved AI policy is in place.",
    },
    {
        "control_id": "ctrl_08",
        "claim_text": "Staff have been trained on responsible AI use.",
    },
    {
        "control_id": "ctrl_09",
        "claim_text": "Model and supplier due diligence has been performed.",
    },
]


def run_tests():
    subprocess.run(
        [
            sys.executable, "-m", "pytest", "tests/",
            "--json-report", f"--json-report-file={REPORT_JSON}", "-q",
        ],
        cwd=ROOT,
    )


def parse_org_and_test(nodeid: str):
    # nodeid like tests/test_telemetry_compliance.py::test_x[org_id]
    func = nodeid.split("::")[-1]
    if "[" in func:
        name, org = func[:-1].split("[")
        return name, org
    return func, "unknown"


def load_declared(org: str) -> dict:
    """Self-assessment answers for one org: {control_id: bool}."""
    path = ROOT / f"declared_{org}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def reconcile(declared: bool | None, test_outcome: str | None) -> str:
    """The only decision logic in the reconciliation engine. Deterministic,
    no LLM in the path -- see reconciliation_mapping_spec.md."""
    if test_outcome is None or test_outcome in ("error", "skipped"):
        return "NOT_OBSERVABLE"   # broken/skipped test gives no signal on the control
    passed = test_outcome == "passed"
    if declared is True:
        return "CONFIRMED" if passed else "CONTRADICTED"
    if declared is False:
        return "UNDERSTATED" if passed else "CONSISTENT_GAP"
    return "NOT_OBSERVABLE"   # declared is None / unanswered


def narrate(rec: dict) -> list[str]:
    """Plain-language reconciliation narration for one control, per
    reconciliation_mapping_spec.md ("What the app should say when it
    runs")."""
    declared_word = {True: "Yes", False: "No", None: "no answer on file"}[rec["declared"]]
    lines = [f"> You reported: **{declared_word}** -- {rec['claim_text']}"]
    if rec["state"] == "NOT_OBSERVABLE":
        if rec["test_outcome"] in ("error", "skipped"):
            lines.append(
                f"> Your telemetry shows: test **{rec['test_outcome']}** -- "
                f"no reliable signal on this control.")
        else:
            lines.append("> Your telemetry shows: no telemetry test exists for this control.")
        lines.append("> Declaration stands alone -- nothing to compare it against.")
    else:
        outcome_word = "passed" if rec["test_outcome"] == "passed" else "failed"
        lines.append(f"> Your telemetry shows: test **{outcome_word}**.")
        agree = rec["state"] in ("CONFIRMED", "CONSISTENT_GAP")
        lines.append(f"> These **{'agree' if agree else 'do not agree'}**.")
    return lines


def build_reconciliation(org: str, results: list[dict]) -> list[dict]:
    """Join test outcomes for one org against its declared answers,
    one record per control, per the Build brief data structure."""
    declared = load_declared(org)
    records = []
    for r in results:
        control_id = r["control_id"]
        if control_id is None:
            # No CLAUSE_MAP entry for this test -- nothing to reconcile
            # against. Still visible as PASS/FAIL in the compliance table
            # above; skip here rather than mislabel a real result NOT_OBSERVABLE.
            continue
        declared_answer = declared.get(control_id)
        records.append({
            "control_id": control_id,
            "claim_text": r["claim_text"],
            "declared": declared_answer,
            "test_name": r["test_name"],
            "clause": r["clause"],
            "test_outcome": r["status"],
            "state": reconcile(declared_answer, r["status"]),
        })
    for c in DECLARATION_ONLY_CONTROLS:
        declared_answer = declared.get(c["control_id"])
        records.append({
            "control_id": c["control_id"],
            "claim_text": c["claim_text"],
            "declared": declared_answer,
            "test_name": None,
            "clause": None,
            "test_outcome": None,
            "state": reconcile(declared_answer, None),
        })
    return records


def build_report():
    data = json.loads(REPORT_JSON.read_text())
    by_org = defaultdict(list)

    for test in data.get("tests", []):
        name, org = parse_org_and_test(test["nodeid"])
        meta = CLAUSE_MAP.get(name, {
            "control_id": None, "control": name,
            "claim_text": None, "clause": "unmapped",
        })
        by_org[org].append({
            "test_name": name,
            "control_id": meta["control_id"],
            "control": meta["control"],
            "claim_text": meta["claim_text"],
            "clause": meta["clause"],
            "status": test["outcome"],
        })

    generated_at = datetime.now(timezone.utc).isoformat()

    RECONCILIATION_LABELS = {
        "CONFIRMED": "✅ Confirmed",
        "CONTRADICTED": "❌ Contradicted",
        "CONSISTENT_GAP": "⚠️ Consistent gap",
        "UNDERSTATED": "ℹ️ Understated",
        "NOT_OBSERVABLE": "— Not observable",
    }

    for org, results in by_org.items():
        lines = [
            f"# AI Act / ISO 42001 Continuous Audit Report",
            f"**Organisation:** {org}  ",
            f"**Generated:** {generated_at}  ",
            f"**Source:** governance-critic-evals / telemetry compliance suite  ",
            "**Data provenance:** Synthetic telemetry (demonstration). The "
            "evaluation logic, clause mapping and reconciliation run "
            "unchanged against live OpenTelemetry spans from an "
            "instrumented system.",
            "**Shadow AI note:** Telemetry only covers instrumented systems. "
            "A clean run here means nothing to report from the systems we "
            "can see -- it is not evidence of the absence of unregistered "
            "AI use elsewhere in the organisation.",
            "**Clause mapping caveat:** The ISO/IEC 42001 clause references "
            "below are a starting mapping, not a certified crosswalk. "
            "Verify each citation against the actual clause text before "
            "this goes in front of a client.\n",
            "| Control | ISO/IEC 42001 Reference | Status |",
            "|---|---|---|",
        ]
        for r in results:
            status = "✅ PASS" if r["status"] == "passed" else "❌ FAIL"
            lines.append(f"| {r['control']} | {r['clause']} | {status} |")

        n_fail = sum(1 for r in results if r["status"] != "passed")
        lines.append("")
        if n_fail:
            lines.append(f"**{n_fail} control(s) require remediation before next audit cycle.**")
        else:
            lines.append("**All monitored controls passing as of this run.**")

        reconciliation = build_reconciliation(org, results)
        lines += [
            "",
            "## Reconciliation: declared vs. observed",
            "",
            "| Control ID | Claim | Declared | Telemetry | State |",
            "|---|---|---|---|---|",
        ]
        for rec in reconciliation:
            declared_str = {True: "Yes", False: "No", None: "—"}[rec["declared"]]
            telemetry_str = {"passed": "PASS", "failed": "FAIL", None: "—"}.get(
                rec["test_outcome"], rec["test_outcome"])
            state_str = RECONCILIATION_LABELS[rec["state"]]
            lines.append(
                f"| {rec['control_id']} | {rec['claim_text']} | "
                f"{declared_str} | {telemetry_str} | {state_str} |")

        contradicted = [rec for rec in reconciliation if rec["state"] == "CONTRADICTED"]
        if contradicted:
            lines += ["", "**Evidence (contradicted controls only):**", ""]
            for rec in contradicted:
                ev = evidence_for(rec["control_id"], org)
                if ev:
                    lines.append(f"- **{rec['control_id']}**:")
                    for line in ev:
                        lines.append(f"  - {line}")
                else:
                    lines.append(f"- **{rec['control_id']}**: no span-level extractor registered.")

        lines += ["", "## What we found, per control", ""]
        for rec in reconciliation:
            lines.append(f"**{rec['control_id']}**")
            lines += narrate(rec)
            lines.append("")

        n_contradicted = sum(1 for rec in reconciliation if rec["state"] == "CONTRADICTED")
        lines.append("")
        if n_contradicted:
            lines.append(
                f"**{n_contradicted} declared control(s) contradicted by "
                f"telemetry -- the gap between design and operating "
                f"effectiveness.**")
        else:
            lines.append("**No declared controls contradicted by telemetry this cycle.**")

        out_path = ROOT / f"audit_report_{org}.md"
        out_path.write_text("\n".join(lines))
        print(f"wrote {out_path}")


if __name__ == "__main__":
    run_tests()
    build_report()
