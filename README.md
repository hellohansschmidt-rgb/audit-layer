# AI Act Continuous Audit Layer

A thin extension of `governance-critic-evals`: turns simulated agent
telemetry into ISO/IEC 42001-mapped audit evidence, continuously, instead
of a once-a-year point-in-time assessment.

## Why this exists

Danish industrial boards asking "how many Copilot seats do we need" are
asking the wrong question. The harder, more valuable one is: can you prove
to an auditor that your AI systems are behaving as intended? Generic
assistants don't produce audit trails. This does.

## Pattern

Same accountability principle as the core Governance Critic Agent: a model
or agent can flag and describe, but a deterministic layer decides. Here,
pytest -- not an LLM -- decides pass/fail against each control.

```
agent telemetry (OTel-shaped spans)
        |
        v
pytest compliance suite  <-- each test maps to a specific 42001 clause
        |
        v
audit_report_<org>.md    <-- what the board actually reads
        |
        v
GitHub Actions CI        <-- makes "continuous" literally true
```

## Status: synthetic telemetry, real evaluation logic

The spans in `telemetry/sample_spans_*.json` are generated, not pulled
from a live agent fleet -- there's no production deployment to instrument
yet. The evaluation logic, clause mapping, and report generation are real
and would run unchanged against real OTel spans from a live system. Be
upfront about this distinction if a technical stakeholder asks; it's a
credibility point, not a weakness, as long as it's not implied otherwise.

## Run it

```bash
pip install pytest pytest-json-report --break-system-packages
python3 telemetry/generate_spans.py     # regenerate fixture spans
python3 generate_audit_report.py        # run tests + build reports
```

Outputs `audit_report_<org>.md` per fixture org.

## Connecting a real assessment

`convert_declared.py` bridges an `ai-governance-assessment` export into this
pipeline:

```
ai-governance-assessment export (JSON)
        |
        v
convert_declared.py    <-- maps 4 of 18 questions to a control, applies a
        |                   score >=2 = "yes" threshold (see mapping_helpful_phoenix.md)
        v
declared_<org>.json
        |
        v
generate_audit_report.py + reconcile()   <-- unchanged, pre-existing
        |
        v
audit_report_<org>.md   <-- reconciliation table + narration
```

```bash
python3 convert_declared.py path/to/readiness_export_<org>.json
python3 generate_audit_report.py
```

**Coverage.** Of the assessment's 18 questions, only 4 map to a control this
repo can actually check against telemetry (PII handling, latency/SLA
monitoring, bias review, audit-trail completeness). The other 14 questions
have no telemetry counterpart and are declaration-only. Separately,
`ctrl_04` (low-confidence human oversight) is a fifth telemetry-backed
control with no assessment question mapped to it today, so it also
resolves as declaration-only in practice -- the same effective outcome as
`ctrl_06`-`ctrl_09`, which are declaration-only controls unrelated to any
specific questionnaire item. See `mapping_helpful_phoenix.md` for the full
mapping and the confidence level (strong/moderate) of each one.

**Provenance and caveats (repeated from above, because this section is
often read on its own):** the telemetry behind this pipeline is synthetic,
not pulled from a live agent fleet -- see "Status: synthetic telemetry, real
evaluation logic" above. The ISO/IEC 42001 clause references in `CLAUSE_MAP`
are a starting mapping, not a certified crosswalk; verify each citation
before this goes in front of a client.

## Before showing this to a client

- [ ] Verify each clause citation in `test_telemetry_compliance.py`
      against the actual ISO/IEC 42001 clause text. The mapping here is a
      starting point, not a certified crosswalk.
- [ ] Swap `FIXTURE_ORGS` in `telemetry/generate_spans.py` for names/tiers
      that match your existing governance-critic-evals fixtures.
- [ ] Wire into the existing GitHub Actions workflow so the report
      regenerates on every push -- this is what makes "continuous" true.
