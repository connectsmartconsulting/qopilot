# Qopilot

**AI Assurance Copilot for aigrc**

[![CI](https://github.com/connectsmartconsulting/qopilot/actions/workflows/ci.yml/badge.svg)](https://github.com/connectsmartconsulting/qopilot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)]()

> **v0.1.0** - Two commands: `author` recommends which aigrc checks to run, `interpret` turns aigrc JSON reports into business-language audit narratives. Works fully offline. LLM-enhanced output available with an Anthropic or OpenAI API key.

Qopilot is the advisory layer on top of [aigrc](https://github.com/connectsmartconsulting/aigrc). It answers two questions:

- **Before a check:** Which aigrc checks should this client run, and why?
- **After a check:** What do these results mean for the risk committee and regulator?

Built by [Connect Smart Consulting Inc.](https://connectsmartconsulting.com) - Ottawa, Ontario, Canada.

---

## Quick start

```bash
git clone https://github.com/connectsmartconsulting/qopilot.git
cd qopilot
pip install -e .
```

---

## Commands

### `qopilot author` — recommend checks for a client system

Takes a plain-language description of the client's AI system and outputs a prioritised list of aigrc checks with regulatory rationale.

```bash
qopilot author --input examples/acme-system.md --offline
```

Output:

```
Provider: offline
Recommendations written to: examples/acme-system.qopilot-recs.md

Recommended checks (3):
  - prompt-injection  [LIVE]  priority: high
  - pii-leakage       [PLANNED]  priority: high
  - topic-boundary    [PLANNED]  priority: medium
```

With an LLM provider:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
qopilot author --input examples/acme-system.md
```

---

### `qopilot interpret` — translate aigrc results into audit narrative

Takes an aigrc JSON report and produces an executive summary, material findings with remediation guidance, and regulatory traceability table.

```bash
# Generate the aigrc report first
aigrc check prompt-injection --target mock://moderate --report-json report.json

# Interpret it
qopilot interpret --report report.json --offline
```

Output:

```
Provider: offline
Narrative written to: report.qopilot-narrative.md

Executive summary: The AI system achieved a 83.3% pass rate against the
18-payload OWASP LLM01 taxonomy. Several attack classes produced successful
bypasses...
Findings: 3
Next engagement: Tier 2 validation engagement recommended...
```

---

## Options

| Flag | Description |
|------|-------------|
| `--input PATH` | (author) Markdown file describing the client system |
| `--report PATH` | (interpret) aigrc JSON report path |
| `--out PATH` | Output path for the generated markdown |
| `--offline` | Use deterministic offline renderer, no API call |

---

## Provider selection

Qopilot auto-detects the available provider in this order:

1. `--offline` flag forces the deterministic renderer
2. `ANTHROPIC_API_KEY` in environment uses Claude
3. `OPENAI_API_KEY` in environment uses GPT-4o-mini
4. No key found falls back to offline renderer

The offline renderer produces engineering-grade output suitable for first drafts and CI. LLM-enhanced output produces richer narratives for client-facing deliverables.

---

## Regulatory grounding

Every recommendation and finding is grounded in specific controls:

- NIST AI RMF (MEASURE 2.6, 2.7, 2.10, 2.11)
- EU AI Act (Articles 10, 15)
- ISO/IEC 42001 (A.6.2.6, A.7.4)
- OWASP LLM Top 10 2025 (LLM01, LLM02, LLM06, LLM07, LLM09, LLM10)
- PIPEDA Principle 4.7

---

## Typical workflow

```bash
# 1. Describe the client system
cat > client-system.md << 'EOF'
A GPT-4o customer service bot for a Canadian lending company.
Handles product questions. Integrates with banking API for account lookups.
Handles customer PII. Expanding to EU in Q3.
EOF

# 2. Get check recommendations
qopilot author --input client-system.md --offline

# 3. Run the recommended checks
aigrc check prompt-injection --target openai://gpt-4o --report-json report.json

# 4. Produce the audit narrative
qopilot interpret --report report.json --offline
```

---

## Roadmap

| Version | Feature | Status | Target |
|---------|---------|--------|--------|
| v0.1.0 | author + interpret, offline renderer | **Live** | Released |
| v0.2.0 | pii-leakage interpretation, multi-check narratives | Planned | Q3 2026 |
| v0.3.0 | Drift narrative, longitudinal comparison | Planned | Q4 2026 |
| v1.0 | Qopilot platform - multi-client, audit packaging | Planned | Q1 2027 |

**RES (Resilience Engineering Scorecard)** - composite scoring layer aggregating aigrc results across all governance layers. Design begins Q3 2026.

---

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v          # 7 tests, offline only, no API key required
ruff check qopilot tests  # lint
```

---

## About

Qopilot is developed by [Connect Smart Consulting Inc.](https://connectsmartconsulting.com), an Ottawa-based consultancy specialising in AI governance validation, cybersecurity assurance, and quality engineering.

The underlying evidence is produced by [aigrc](https://github.com/connectsmartconsulting/aigrc).

- Website: [connectsmartconsulting.com](https://connectsmartconsulting.com)
- Contact: safiuddin@connectsmartconsulting.com

---

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Connect Smart Consulting Inc.
