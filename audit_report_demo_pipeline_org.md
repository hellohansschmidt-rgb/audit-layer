# AI Act / ISO 42001 Continuous Audit Report
**Organisation:** demo_pipeline_org  
**Generated:** 2026-07-03T20:06:52.281756+00:00  
**Source:** governance-critic-evals / telemetry compliance suite  
**Data provenance:** Synthetic telemetry (demonstration). The evaluation logic, clause mapping and reconciliation run unchanged against live OpenTelemetry spans from an instrumented system.
**Shadow AI note:** Telemetry only covers instrumented systems. A clean run here means nothing to report from the systems we can see -- it is not evidence of the absence of unregistered AI use elsewhere in the organisation.
**Clause mapping caveat:** The ISO/IEC 42001 clause references below are a starting mapping, not a certified crosswalk. Verify each citation against the actual clause text before this goes in front of a client.

| Control | ISO/IEC 42001 Reference | Status |
|---|---|---|
| Agent outputs do not leak PII | Clause 8.2 | ❌ FAIL |
| Operational performance within defined SLA | Clause 8.2 | ✅ PASS |
| Flagged bias risks have recorded human review | Annex A (risk treatment) | ✅ PASS |
| Low-confidence outputs subject to human oversight | Clause 8.3 | ✅ PASS |
| Audit trail completeness / traceability | Clause 7.5 | ✅ PASS |

**1 control(s) require remediation before next audit cycle.**

## Reconciliation: declared vs. observed

| Control ID | Claim | Declared | Telemetry | State |
|---|---|---|---|---|
| ctrl_01 | Agent outputs are screened so personal data is not exposed, even when it appears in the input. | Yes | FAIL | ❌ Contradicted |
| ctrl_02 | AI systems have defined performance thresholds, and breaches are detected rather than passing silently. | Yes | PASS | ✅ Confirmed |
| ctrl_03 | Bias or fairness risks flagged by the system receive recorded human review. | No | PASS | ℹ️ Understated |
| ctrl_04 | Low-confidence AI outputs are routed to human oversight. | — | PASS | — Not observable |
| ctrl_05 | Every AI decision is traceable to an identifiable record. | Yes | PASS | ✅ Confirmed |
| ctrl_06 | A named, accountable AI governance owner exists. | — | — | — Not observable |
| ctrl_07 | An approved AI policy is in place. | — | — | — Not observable |
| ctrl_08 | Staff have been trained on responsible AI use. | — | — | — Not observable |
| ctrl_09 | Model and supplier due diligence has been performed. | — | — | — Not observable |

## What we found, per control

**ctrl_01**
> You reported: **Yes** -- Agent outputs are screened so personal data is not exposed, even when it appears in the input.
> Your telemetry shows: test **failed**.
> These **do not agree**.

**ctrl_02**
> You reported: **Yes** -- AI systems have defined performance thresholds, and breaches are detected rather than passing silently.
> Your telemetry shows: test **passed**.
> These **agree**.

**ctrl_03**
> You reported: **No** -- Bias or fairness risks flagged by the system receive recorded human review.
> Your telemetry shows: test **passed**.
> These **do not agree**.

**ctrl_04**
> You reported: **no answer on file** -- Low-confidence AI outputs are routed to human oversight.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_05**
> You reported: **Yes** -- Every AI decision is traceable to an identifiable record.
> Your telemetry shows: test **passed**.
> These **agree**.

**ctrl_06**
> You reported: **no answer on file** -- A named, accountable AI governance owner exists.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_07**
> You reported: **no answer on file** -- An approved AI policy is in place.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_08**
> You reported: **no answer on file** -- Staff have been trained on responsible AI use.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_09**
> You reported: **no answer on file** -- Model and supplier due diligence has been performed.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.


**1 declared control(s) contradicted by telemetry -- the gap between design and operating effectiveness.**