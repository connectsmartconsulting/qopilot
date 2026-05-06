# Roadmap

## v0.1.0 (released May 2026) - current

`author` and `interpret` commands working end to end. Deterministic offline renderer (no API key required). LLM-enhanced output via Anthropic and OpenAI-compatible providers. 7 tests passing.

## v0.2 (target Q3 2026)

- `qopilot compare` - diff two aigrc reports (before / after remediation)
- PDF export via weasyprint (optional dependency)
- Custom prompt override (point Qopilot at your own prompt template)

## v0.3 (target Q4 2026)

- `qopilot trend` - analyse a time series of aigrc reports for drift detection
- DOCX export for client deliverables that require Word format
- Templating hooks so consultancies can brand the output
- RES (Resilience Engineering Scorecard) narrative - Qopilot interpret layer for composite resilience scores produced by aigrc RES module. Design begins Q3 2026 after first client engagement.

## v0.4 (target Q1 2027)

- MCP server exposing author / interpret as tools to Claude, GPT, and other agents
- Integration with GitHub Issues to open remediation tickets directly from findings

## Non-goals

- Hosted SaaS version (out of scope for open source; proprietary deliveries remain via Connect Smart engagements)
- Replacement for human risk judgement (Qopilot drafts; humans sign off)
