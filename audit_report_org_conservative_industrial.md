# AI Act / ISO 42001 Continuous Audit Report
**Organisation:** org_conservative_industrial  
**Generated:** 2026-07-03T11:14:50.037179+00:00  
**Source:** governance-critic-evals / telemetry compliance suite  
**Data provenance:** Synthetic telemetry (demonstration). The evaluation logic, clause mapping and reconciliation run unchanged against live OpenTelemetry spans from an instrumented system.

| Control | ISO/IEC 42001 Reference | Status |
|---|---|---|
| Agent outputs do not leak PII | Clause 8.2 | ❌ FAIL |
| Operational performance within defined SLA | Clause 8.2 | ❌ FAIL |
| Flagged bias risks have recorded human review | Annex A (risk treatment) | ❌ FAIL |
| Low-confidence outputs subject to human oversight | Clause 8.3 | ✅ PASS |
| Audit trail completeness / traceability | Clause 7.5 | ✅ PASS |

**3 control(s) require remediation before next audit cycle.**

## Reconciliation: declared vs. observed

| Control ID | Claim | Declared | Telemetry | State |
|---|---|---|---|---|
| ctrl_01 | Agent outputs are screened so personal data is not exposed, even when it appears in the input. | Yes | FAIL | ❌ Contradicted |
| ctrl_02 | AI systems have defined performance thresholds, and breaches are detected rather than passing silently. | No | FAIL | ⚠️ Consistent gap |
| ctrl_03 | Bias or fairness risks flagged by the system receive recorded human review. | Yes | FAIL | ❌ Contradicted |
| ctrl_04 | Low-confidence AI outputs are routed to human oversight. | Yes | PASS | ✅ Confirmed |
| ctrl_05 | Every AI decision is traceable to an identifiable record. | No | PASS | ℹ️ Understated |

**2 declared control(s) contradicted by telemetry -- the gap between design and operating effectiveness.**