"""
test_convert_declared.py

Unit tests for convert_declared.convert() -- the pure mapping+threshold
function. No filesystem I/O here; see mapping_helpful_phoenix.md for the
question -> control_id rationale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from convert_declared import convert, MAPPING, DECLARED_THRESHOLD


def _export_with_scores(scores: dict) -> dict:
    """Minimal export payload with the given {question_id: score}."""
    by_domain = {}
    for qid, score in scores.items():
        domain_id = qid.rsplit("_q", 1)[0]
        by_domain.setdefault(domain_id, []).append({"id": qid, "score": score})
    return {
        "organisation": "Test Org",
        "domains": [
            {"id": d, "name": d, "questions": qs, "total": sum(q["score"] for q in qs)}
            for d, qs in by_domain.items()
        ],
    }


def test_score_3_declares_true():
    export = _export_with_scores({"data_governance_q2": 3})
    assert convert(export)["ctrl_01"] is True


def test_score_1_declares_false():
    export = _export_with_scores({"data_governance_q2": 1})
    assert convert(export)["ctrl_01"] is False


def test_score_2_boundary_declares_true():
    export = _export_with_scores({"data_governance_q2": DECLARED_THRESHOLD})
    assert convert(export)["ctrl_01"] is True


def test_unmapped_question_produces_no_control():
    export = _export_with_scores({"transparency_explainability_q1": 3})
    declared = convert(export)
    assert "ctrl_04" not in declared
    assert set(declared.keys()) <= set(MAPPING.values())


def test_all_four_mapped_controls_present_when_all_answered():
    export = _export_with_scores({
        "data_governance_q2": 3,
        "risk_management_q2": 0,
        "ethics_fairness_q1": 2,
        "compliance_audit_q3": 1,
    })
    declared = convert(export)
    assert declared == {
        "ctrl_01": True,
        "ctrl_02": False,
        "ctrl_03": True,
        "ctrl_05": False,
    }


from convert_declared import foundation_tier_warning


def test_foundation_fail_produces_warning_naming_the_tier():
    export = _export_with_scores({"data_governance_q2": 3})
    export["foundation"] = {"status": "FAIL"}
    export["maturityTier"] = "Established"
    export["organisation"] = "Test Org"
    warning = foundation_tier_warning(export)
    assert warning is not None
    assert "FAIL" in warning
    assert "Established" in warning
    assert "Test Org" in warning


def test_foundation_pass_produces_no_warning():
    export = _export_with_scores({"data_governance_q2": 3})
    export["foundation"] = {"status": "PASS"}
    assert foundation_tier_warning(export) is None


def test_foundation_weak_produces_no_warning():
    # WEAK caps the tier but does not withhold it -- only FAIL warrants
    # the "not a valid rating" warning, per Foundation_Gate_Spec_v1.md.
    export = _export_with_scores({"data_governance_q2": 3})
    export["foundation"] = {"status": "WEAK"}
    assert foundation_tier_warning(export) is None


def test_convert_output_unaffected_by_foundation_status_or_tier():
    # convert() must derive declared answers purely from domain scores --
    # a FAIL status and a misleadingly high tier must not change the output.
    export = _export_with_scores({"data_governance_q2": 3})
    export["foundation"] = {"status": "FAIL"}
    export["maturityTier"] = "Leading"
    assert convert(export) == {"ctrl_01": True}
