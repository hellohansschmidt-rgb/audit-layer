# AI Act / ISO 42001 Continuous Audit Report
**Organisation:** org_regulated_finance  
**Generated:** 2026-07-04T05:28:14.744858+00:00  
**Source:** governance-critic-evals / telemetry compliance suite  
**Data provenance:** Synthetic telemetry (demonstration). The evaluation logic, clause mapping and reconciliation run unchanged against live OpenTelemetry spans from an instrumented system.
**Shadow AI note:** Telemetry only covers instrumented systems. A clean run here means nothing to report from the systems we can see -- it is not evidence of the absence of unregistered AI use elsewhere in the organisation.
**Clause mapping caveat:** The ISO/IEC 42001 clause references below are a starting mapping, not a certified crosswalk. Verify each citation against the actual clause text before this goes in front of a client.

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
| ctrl_01 | Agent outputs are screened so personal data is not exposed, even when it appears in the input. | Yes | FAIL | ❌ Contradicted |
| ctrl_02 | AI systems have defined performance thresholds, and breaches are detected rather than passing silently. | Yes | FAIL | ❌ Contradicted |
| ctrl_03 | Bias or fairness risks flagged by the system receive recorded human review. | Yes | PASS | ✅ Confirmed |
| ctrl_04 | Low-confidence AI outputs are routed to human oversight. | Yes | PASS | ✅ Confirmed |
| ctrl_05 | Every AI decision is traceable to an identifiable record. | Yes | PASS | ✅ Confirmed |
| ctrl_06 | A named, accountable AI governance owner exists. | Yes | — | — Not observable |
| ctrl_07 | An approved AI policy is in place. | Yes | — | — Not observable |
| ctrl_08 | Staff have been trained on responsible AI use. | Yes | — | — Not observable |
| ctrl_09 | Model and supplier due diligence has been performed. | Yes | — | — Not observable |

**Evidence (contradicted controls only):**

- **ctrl_01**:
  - span `96ea94a226414743` (trace `6b27e4bae16e4023ba79b99cbc765d53`): `output_contains_pii=True`
  - span `fea33d613a3b48dd` (trace `eb34f98eac3f4a93a59a81a911ac1e6a`): `output_contains_pii=True`
- **ctrl_02**:
  - span `41297265e1a641a1` (trace `9ccd60fb7e0b438fb3ab14f3b29615d5`): latency_ms=2902 > latency_sla_ms=2000 (Δ+902ms)

## What we found, per control

**ctrl_01**
> You reported: **Yes** -- Agent outputs are screened so personal data is not exposed, even when it appears in the input.
> Your telemetry shows: test **failed**.
> These **do not agree**.

**ctrl_02**
> You reported: **Yes** -- AI systems have defined performance thresholds, and breaches are detected rather than passing silently.
> Your telemetry shows: test **failed**.
> These **do not agree**.

**ctrl_03**
> You reported: **Yes** -- Bias or fairness risks flagged by the system receive recorded human review.
> Your telemetry shows: test **passed**.
> These **agree**.

**ctrl_04**
> You reported: **Yes** -- Low-confidence AI outputs are routed to human oversight.
> Your telemetry shows: test **passed**.
> These **agree**.

**ctrl_05**
> You reported: **Yes** -- Every AI decision is traceable to an identifiable record.
> Your telemetry shows: test **passed**.
> These **agree**.

**ctrl_06**
> You reported: **Yes** -- A named, accountable AI governance owner exists.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_07**
> You reported: **Yes** -- An approved AI policy is in place.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_08**
> You reported: **Yes** -- Staff have been trained on responsible AI use.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.

**ctrl_09**
> You reported: **Yes** -- Model and supplier due diligence has been performed.
> Your telemetry shows: no telemetry test exists for this control.
> Declaration stands alone -- nothing to compare it against.


**2 declared control(s) contradicted by telemetry -- the gap between design and operating effectiveness.**