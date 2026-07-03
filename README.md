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

## Before showing this to a client

- [ ] Verify each clause citation in `test_telemetry_compliance.py`
      against the actual ISO/IEC 42001 clause text. The mapping here is a
      starting point, not a certified crosswalk.
- [ ] Swap `FIXTURE_ORGS` in `telemetry/generate_spans.py` for names/tiers
      that match your existing governance-critic-evals fixtures.
- [ ] Wire into the existing GitHub Actions workflow so the report
      regenerates on every push -- this is what makes "continuous" true.
