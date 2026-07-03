# Mapping: ai-governance-assessment → audit-layer controls

**Extends:** `reconciliation_mapping_spec.md`
**Status:** implemented in `convert_declared.py`

Of the 18 questions in `ai-governance-assessment` (self-reported maturity,
scored 0–3 per question), 4 have a defensible mapping to a telemetry-backed
control already defined in `generate_audit_report.py`'s `CLAUSE_MAP`. The
rest are legitimately declaration-only, same as `ctrl_06`–`ctrl_09`.

| Question id | Question (top-score option, paraphrased) | control_id | Claim it evidences | Confidence |
|---|---|---|---|---|
| `data_governance_q2` | Personal data protection in AI systems (full PII inventory, consent tracking, automated minimisation) | `ctrl_01` | Agent outputs are screened so personal data is not exposed. | Strong — direct match. |
| `risk_management_q2` | AI monitoring/incident process (continuous monitoring, automated alerts, rapid SLAs) | `ctrl_02` | AI systems have defined performance thresholds; breaches are detected. | Moderate — this question is about incident monitoring generally, not model latency specifically. Treat this mapping as a proxy, not a literal restatement. |
| `ethics_fairness_q1` | Bias testing (continuous bias monitoring with fairness metrics dashboards) | `ctrl_03` | Flagged bias/fairness risks receive recorded human review. | Strong — direct match. |
| `compliance_audit_q3` | AI system inventory (comprehensive registry with metadata, audit trails) | `ctrl_05` | Every AI decision is traceable to an identifiable record. | Moderate — this question is about system-level inventory/audit trails, not per-decision span completeness. Treat as a proxy. |

## Explicitly not mapped

- **`ctrl_04`** (low-confidence outputs routed to human oversight) — no question
  in the current 18-question assessment asks about confidence-based routing.
  Every export through this pipeline leaves `ctrl_04` unanswered, so
  `reconcile()` correctly returns `NOT_OBSERVABLE` for it regardless of
  telemetry outcome. This is honest, not a gap in the converter — closing it
  requires a new question in `ai-governance-assessment`, out of scope here.
- **`ctrl_06`–`ctrl_09`** (owner, policy, training, due diligence) — declaration-only
  controls that predate this integration and aren't tied to a specific
  questionnaire item. Left as-is.
- The other 14 assessment questions — no telemetry test exists for what they ask
  (e.g. governance committee structure, ethics board existence, regulatory
  tracking). They remain valuable as self-reported maturity signal but have no
  reconciliation counterpart.

## Threshold

A mapped question's `0–3` score converts to a boolean declared answer:
**score ≥ 2 → `true`** ("yes, we do this"), **score 0–1 → `false`**.

## Foundation status gates the maturity tier — reconciliation does not override it

The export's `foundation.status` field carries the Foundation Gate verdict
(`PASS` / `WEAK` / `FAIL`) computed by `ai-governance-assessment` before any
domain question is scored — see `Foundation_Gate_Spec_v1.md` Part 3 in that
repo. That verdict is a precondition on the whole assessment, not one more
data point to reconcile.

**If `foundation.status` is `FAIL`, `maturityTier` in the export must not be
treated as a valid rating anywhere downstream** — not in `convert_declared.py`,
not in any report or dashboard built on top of this pipeline. The organisation
hadn't earned a tier in the source assessment (the tool withholds it there
for exactly this reason); reconciliation re-labelling raw domain answers as a
"tier" would silently undo that. Domain scores are still safe to run through
the `MAPPING`/threshold logic above unchanged — the FAIL gate is about the
tier label, not about whether individual questions can still be reconciled
against telemetry.

Any future consumer of `maturityTier` (e.g. a dashboard) must check
`foundation.status` first and render the raw score as a provisional
diagnostic, per the source spec's own report copy, rather than a tier, when
status is `FAIL`. `convert_declared.py` itself never reads `maturityTier`, so
this constraint doesn't change its code — it's here so nothing built later
on top of `declared_<org>.json` or the raw export re-introduces a tier the
source tool deliberately withheld.
