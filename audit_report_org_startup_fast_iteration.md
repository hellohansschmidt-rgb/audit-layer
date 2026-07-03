# AI Act / ISO 42001 Continuous Audit Report
**Organisation:** org_startup_fast_iteration  
**Generated:** 2026-07-03T12:00:11.245096+00:00  
**Source:** governance-critic-evals / telemetry compliance suite  
**Data provenance:** Synthetic telemetry (demonstration). The evaluation logic, clause mapping and reconciliation run unchanged against live OpenTelemetry spans from an instrumented system.
**Shadow AI note:** Telemetry only covers instrumented systems. A clean run here means nothing to report from the systems we can see -- it is not evidence of the absence of unregistered AI use elsewhere in the organisation.

| Control | ISO/IEC 42001 Reference | Status |
|---|---|---|
| Agent outputs do not leak PII | Clause 8.2 | ❌ FAIL |
| Operational performance within defined SLA | Clause 8.2 | ❌ FAIL |
| Flagged bias risks have recorded human review | Annex A (risk treatment) | ✅ PASS |
| Low-confidence outputs subject to human oversight | Clause 8.3 | ✅ PASS |
| Audit trail completeness / traceability | Clause 7.5 | ✅ PASS |

**2 control(s) require remediation before next audit cycle.**

## Reconciliation: declared vs. observed

| Control ID | Claim | Declared | Telemetry | State |
|---|---|---|---|---|
| ctrl_01 | Agent outputs are screened so personal data is not exposed, even when it appears in the input. | No | FAIL | ⚠️ Consistent gap |
| ctrl_02 | AI systems have defined performance thresholds, and breaches are detected rather than passing silently. | No | FAIL | ⚠️ Consistent gap |
| ctrl_03 | Bias or fairness risks flagged by the system receive recorded human review. | No | PASS | ℹ️ Understated |
| ctrl_04 | Low-confidence AI outputs are routed to human oversight. | No | PASS | ℹ️ Understated |
| ctrl_05 | Every AI decision is traceable to an identifiable record. | Yes | PASS | ✅ Confirmed |
| ctrl_06 | A named, accountable AI governance owner exists. | No | — | — Not observable |
| ctrl_07 | An approved AI policy is in place. | No | — | — Not observable |
| ctrl_08 | Staff have been trained on responsible AI use. | No | — | — Not observable |
| ctrl_09 | Model and supplier due diligence has been performed. | No | — | — Not observable |

## What we found, per control

**ctrl_01**
> You reported: **No** -- Agent outputs are screened so personal data is not exposed, even when it appears in the input.
> Your telemetry shows: test **failed**.
> These **agree**.

**ctrl_02**
> You reported: **No** -- AI systems have defined performance thresholds, and breaches are detected rather than passing silently.
> Your telemetry shows: test **failed**.
> These **agree**.

**ctrl_03**
> You reported: **No** -- Bias or fairness risks flagged by the system receive recorded human review.
> Your telemetry shows: test **passed**.
> These **do not agree**.

**ctrl_04**
> You reported: **No** -- Low-confidence AI outputs are routed to human oversight.
> Your telemetry shows: test **passed**.
> These **do not agree**.

**ctrl_05**
> You reported: **Yes** -- Every AI decision is traceable to an identifiable record.
> Your telemetry shows: test **passed**.
> These **agree**.

**ctrl_06**
> You reported: **No** -- A named, accountable AI governance owner exists.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_07**
> You reported: **No** -- An approved AI policy is in place.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_08**
> You reported: **No** -- Staff have been trained on responsible AI use.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_09**
> You reported: **No** -- Model and supplier due diligence has been performed.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.


**No declared controls contradicted by telemetry this cycle.**