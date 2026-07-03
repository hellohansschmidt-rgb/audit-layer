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

# test function name -> (short control description, ISO 42001 clause)
CLAUSE_MAP = {
    "test_no_unredacted_pii_in_outputs": (
        "Agent outputs do not leak PII", "Clause 8.2"),
    "test_latency_within_sla": (
        "Operational performance within defined SLA", "Clause 8.2"),
    "test_bias_terms_flagged_and_reviewed": (
        "Flagged bias risks have recorded human review", "Annex A (risk treatment)"),
    "test_model_confidence_above_floor": (
        "Low-confidence outputs subject to human oversight", "Clause 8.3"),
    "test_spans_have_required_audit_fields": (
        "Audit trail completeness / traceability", "Clause 7.5"),
}


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


def build_report():
    data = json.loads(REPORT_JSON.read_text())
    by_org = defaultdict(list)

    for test in data.get("tests", []):
        name, org = parse_org_and_test(test["nodeid"])
        control, clause = CLAUSE_MAP.get(name, (name, "unmapped"))
        by_org[org].append({
            "control": control,
            "clause": clause,
            "status": test["outcome"],
        })

    generated_at = datetime.now(timezone.utc).isoformat()

    for org, results in by_org.items():
        lines = [
            f"# AI Act / ISO 42001 Continuous Audit Report",
            f"**Organisation:** {org}  ",
            f"**Generated:** {generated_at}  ",
            f"**Source:** governance-critic-evals / telemetry compliance suite\n",
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

        out_path = ROOT / f"audit_report_{org}.md"
        out_path.write_text("\n".join(lines))
        print(f"wrote {out_path}")


if __name__ == "__main__":
    run_tests()
    build_report()
