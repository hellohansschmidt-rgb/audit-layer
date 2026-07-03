# Reconciliation Mapping Spec

**Component:** Continuous Audit Layer — reconciliation engine
**Extends:** `governance-critic-evals` / telemetry compliance suite
**Status:** design spec, ready to build

## What this is for

The readiness assessment captures what an organisation *says* about its AI
governance. The telemetry suite captures what its systems *actually do*. On
their own, those are two separate reports. This spec defines the layer that
puts them side by side and states, per control, whether they agree.

The point of the tool is the disagreement. A declared control that the
telemetry contradicts is the gap between design effectiveness and operating
effectiveness — the finding an auditor cares about most, and the one a
questionnaire alone can never surface.

Same principle as the rest of the repo: the model can flag and describe, but
a deterministic function decides the state. Reconciliation is code, not
judgement.

## Reconciliation states

Each control resolves to one state. The first three are the ones you asked
for; the last two cover the honest case where the org declared *No*.

| State | Declared | Telemetry | Meaning |
|---|---|---|---|
| CONFIRMED | Yes | PASS | Claim backed by observed behaviour. |
| CONTRADICTED | Yes | FAIL | Claim not borne out. This is the finding. |
| CONSISTENT GAP | No | FAIL | Org honestly reports a gap; telemetry confirms it. Remediation item, not a contradiction. |
| UNDERSTATED | No | PASS | System does better than claimed. Low risk, worth surfacing — the org may not know its own control works. |
| NOT OBSERVABLE | any | (no test) | Questionnaire item with no telemetry counterpart. Declaration stands alone. |

## The deterministic rule

This is the whole decision. No LLM in the path.

```python
def reconcile(declared: bool | None, test_outcome: str | None) -> str:
    if test_outcome is None or test_outcome in ("error", "skipped"):
        return "NOT_OBSERVABLE"   # broken/skipped test gives no signal on the control
    passed = test_outcome == "passed"
    if declared is True:
        return "CONFIRMED" if passed else "CONTRADICTED"
    if declared is False:
        return "UNDERSTATED" if passed else "CONSISTENT_GAP"
    return "NOT_OBSERVABLE"   # declared is None / unanswered
```

## The mapping

Each row links one self-assessment claim to the telemetry test that evidences
it, the span attribute the test reads, and the ISO clause it maps to.

Claim wording below is written for the questionnaire side — adjust to match
the actual item text in the live assessment tool.

| # | Self-assessment claim (declared) | Telemetry test | Span attribute | ISO 42001 |
|---|---|---|---|---|
| 1 | Agent outputs are screened so personal data is not exposed, even when it appears in the input. | `test_no_unredacted_pii_in_outputs` | `output_contains_pii` | Clause 8.2 |
| 2 | AI systems have defined performance thresholds, and breaches are detected rather than passing silently. | `test_latency_within_sla` | `latency_ms` vs `latency_sla_ms` | Clause 8.2 |
| 3 | Bias or fairness risks flagged by the system receive recorded human review. | `test_bias_terms_flagged_and_reviewed` | `flagged_bias_terms` + `bias_review_status` | Annex A (risk treatment) |
| 4 | Low-confidence AI outputs are routed to human oversight. | `test_model_confidence_above_floor` | `model_confidence` vs floor (0.65) | Clause 8.3 |
| 5 | Every AI decision is traceable to an identifiable record. | `test_spans_have_required_audit_fields` | `trace_id`, `span_id`, `timestamp`, `agent_id` | Clause 7.5 |

**Worked example — control 4.** Org answers *Yes* to "we route low-confidence
decisions to human review." `test_model_confidence_above_floor` fails: three
spans fell below the confidence floor with no review flag. Reconciliation
returns CONTRADICTED. The report reads:

> Declared: human oversight of low-confidence outputs in place.
> Observed: 3 low-confidence decisions bypassed review last cycle.
> Status: **Contradicted.**

## Not observable in telemetry

Be explicit about the boundary. Telemetry validates only the operational
subset of the questionnaire — the controls that leave a trace in behaviour.
These items are declaration-only; no span will ever confirm or deny them:

- A named, accountable AI governance owner exists.
- An approved AI policy is in place.
- Staff have been trained on responsible AI use.
- Model and supplier due diligence has been performed.

That subset is smaller than the full assessment. It is also exactly where
self-reports are least reliable, so it carries the most weight. Say this
plainly in the output rather than implying the telemetry validates
everything.

**One trap to avoid — shadow AI.** Telemetry only sees systems that are
instrumented. An ungoverned tool nobody registered produces no spans at all.
The absence of spans is not evidence of the absence of AI use. Do not let a
clean telemetry run be read as "no shadow AI" — it means "nothing to report
from the systems we can see." This is the same blind spot the assessment
tool's shadow-AI probe is built to catch; the two are complementary, not
redundant.

## What the app should say when it runs

Narrate both streams and the reconciliation in plain language, per control:

> You reported: [claim].
> Your telemetry shows: [result].
> These **agree** / **do not agree**.

And carry the provenance note on the artifact itself, not only in the README:

> **Data provenance:** Synthetic telemetry (demonstration). The evaluation
> logic, clause mapping and reconciliation run unchanged against live
> OpenTelemetry spans from an instrumented system.

## Build brief for Claude Code

Data structure — one record per control:

```python
{
    "control_id": "ctrl_04",
    "claim_text": "Low-confidence AI outputs are routed to human oversight.",
    "declared": True,            # from the assessment answer
    "test_name": "test_model_confidence_above_floor",
    "clause": "Clause 8.3",
    "test_outcome": "failed",    # from pytest json report, or None
    "state": "CONTRADICTED",     # computed by reconcile()
}
```

Build order:
1. Extend `CLAUSE_MAP` in `generate_audit_report.py` so each test also carries
   its `claim_text` and `control_id`.
2. Add a declared-answers input — a small JSON per org
   (`declared_<org>.json`) holding `{control_id: bool}`. For the demo, hand-
   author these so at least one CONTRADICTED case shows.
3. Add `reconcile()` and run it over the joined test outcomes + declared
   answers.
4. Extend the report: a Reconciliation column (or a second table) rendering
   the state per control, plus the provenance line.
5. Keep the existing pytest suite untouched — reconciliation reads its JSON
   output, it does not replace it.

## Caveat carried from the README

The ISO clause references here are a starting mapping, not a certified
crosswalk. Verify each citation against the actual clause text before this
goes in front of a client. Conservative boards are exactly the audience that
will have someone check.
