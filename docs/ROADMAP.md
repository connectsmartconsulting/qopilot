# Roadmap

Honest delivery plan. Dates are intent, not commitments.

## v0.1.0 (released May 2026) - current

`author` and `interpret` commands working end to end. Deterministic offline renderer (no API key required). LLM-enhanced output via Anthropic and OpenAI-compatible providers. 7 tests passing.

Telecom narrative path live from v0.1.0: `interpret` detects CRTC, 3GPP, and ETSI frameworks in aigrc reports and produces CRTC consumer protection framing, EU AI Act Article 50 language, TM Forum eTOM remediation vocabulary, and 3GPP TS 28.105 human oversight context automatically.

## v0.2 (target Q3 2026)

- `--vertical telecom` flag -- explicit telecom mode for `author` and `interpret` commands. Telecom-specific prompt template, CRTC-ready binder preamble, 3GPP context paragraph naming the governing Release and design-time mandate.
- `qopilot compare` -- diff two aigrc reports (before/after remediation). Shows delta in pass rate, technique failures, and regulatory status.
- topic-boundary check interpretation -- narrative support for the aigrc v0.2 topic-boundary check. CRTC and TM Forum eTOM framing included.
- First public release to PyPI.

## v0.3 (target Q4 2026)

- RES (Resilience Engineering Scorecard) narrative -- Qopilot interpret layer for composite resilience scores produced by aigrc RES module. Includes RES Telecom Profile variant with Critical weighting on PII leakage and human-override dimensions.
- `qopilot trend` -- analyse a time series of aigrc reports for drift detection. CRTC reporting timeline guidance when drift triggers notification obligation.
- DOCX export for client deliverables that require Word format.

## v0.4 (target Q1 2027)

- Qopilot platform beta -- multi-client dashboard, continuous monitoring, telecom vertical dashboard, CRTC audit-readiness indicator.
- MCP server exposing author/interpret as tools to Claude, GPT, and other agents.
- Integration with GitHub Issues to open remediation tickets directly from findings.

## Non-goals

- Hosted SaaS version (out of scope for open source; proprietary deliveries remain via Connect Smart engagements)
- Replacement for human risk judgement (Qopilot drafts; humans sign off)
