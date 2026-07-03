"""
convert_declared.py

Converts an ai-governance-assessment JSON export into a declared_<org>.json
file consumable by generate_audit_report.py's reconciliation engine. See
mapping_helpful_phoenix.md for which questions map to which control_id and
why the mapping stops at 4 controls.

Usage:
    python3 convert_declared.py <export.json> [--org-slug NAME]
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent

# ai-governance-assessment question id -> audit-layer control_id.
# Only questions with a genuine telemetry counterpart are listed here --
# see mapping_helpful_phoenix.md for the full rationale, including why
# ctrl_04 has no entry.
MAPPING = {
    "data_governance_q2": "ctrl_01",
    "risk_management_q2": "ctrl_02",
    "ethics_fairness_q1": "ctrl_03",
    "compliance_audit_q3": "ctrl_05",
}

# A domain-question score of 2 or 3 counts as "yes, we do this" once
# converted to the boolean declared answer the reconciliation engine reads.
DECLARED_THRESHOLD = 2


def slugify(name: str) -> str:
    return re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", name.lower()))


def convert(export: dict) -> dict:
    """Build the {control_id: bool} dict for one assessment export.

    Deliberately reads only export["domains"] -- never export["maturityTier"]
    or export["foundation"]. Control declarations are derived from raw domain
    scores regardless of Foundation Gate status; see foundation_tier_warning()
    for the separate, explicit handling of the FAIL case."""
    scores_by_question = {
        q["id"]: q["score"]
        for domain in export["domains"]
        for q in domain["questions"]
    }
    declared = {}
    for question_id, control_id in MAPPING.items():
        if question_id not in scores_by_question:
            continue
        declared[control_id] = scores_by_question[question_id] >= DECLARED_THRESHOLD
    return declared


def foundation_tier_warning(export: dict) -> str | None:
    """Foundation Gate rule (Foundation_Gate_Spec_v1.md Part 3;
    mapping_helpful_phoenix.md 'Foundation status gates the maturity tier'):
    on FAIL, the source tool withholds the tier entirely -- it is not a
    valid rating. This converter never reads maturityTier when building
    declared answers (see convert() above); this function exists so a FAIL
    export says so loudly instead of silently proceeding, in case a caller
    or a future script is tempted to read maturityTier off the same file.

    Returns a warning string if foundation.status is FAIL, else None.
    """
    status = export.get("foundation", {}).get("status")
    if status == "FAIL":
        tier = export.get("maturityTier", "unknown")
        org = export.get("organisation", "unknown")
        return (
            f"WARNING: foundation.status is FAIL for '{org}'. "
            f"maturityTier ('{tier}') is NOT a valid rating and must not be "
            f"used anywhere downstream. Control declarations below are "
            f"computed from domain scores independently of this and are "
            f"unaffected."
        )
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("export_path", type=Path)
    parser.add_argument("--org-slug", default=None)
    args = parser.parse_args()

    export = json.loads(args.export_path.read_text())

    warning = foundation_tier_warning(export)
    if warning:
        print(warning, file=sys.stderr)

    declared = convert(export)
    org_slug = args.org_slug or slugify(export["organisation"])

    out_path = ROOT / f"declared_{org_slug}.json"
    out_path.write_text(json.dumps(declared, indent=4))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
