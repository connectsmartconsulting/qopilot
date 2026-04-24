# Qopilot

**AI copilot for AI assurance.**

Qopilot is the AI layer that sits alongside [aigrc](https://github.com/connectsmartconsulting/aigrc). It does two things:

1. **`qopilot author`** reads a plain-English description of a client's AI system and recommends which aigrc checks to run, with regulatory rationale.
2. **`qopilot interpret`** reads an aigrc JSON report and produces a business-language audit narrative with prioritised remediation guidance.

Built on four principles drawn from two decades of quality engineering:

1. Fail explicitly, never silently.
2. Every output is reproducible given the same input and model.
3. Human-readable and machine-readable outputs are produced in parallel.
4. CI-native by default, no hosted service required.

Maintained by [Connect Smart Consulting Inc.](https://github.com/connectsmartconsulting).

## Why a separate tool?

aigrc executes checks and produces deterministic evidence. That evidence is auditable but not narrative. It says "15 of 18 payloads passed". It does not say "your bot leaks its system prompt under base64 framing, which creates regulatory exposure under EU AI Act Article 15 and should be remediated by adding a refusal pattern for encoded instructions".

Qopilot is where that translation happens. Keeping it separate means:

- aigrc remains deterministic and reproducible for audit defensibility.
- The LLM calls (which introduce cost and non-determinism) are opt-in.
- Clients with strict data-residency requirements can run aigrc without ever invoking an external model.

## Honest v0.1 scope

Two commands, end to end, working against the Anthropic API or any OpenAI-compatible endpoint. Offline deterministic mode available for testing and demos.

| Capability | Status |
|---|---|
| `qopilot author` - recommend aigrc checks from system description | Live |
| `qopilot interpret` - business narrative + remediation from aigrc report | Live |
| Anthropic API provider | Live |
| OpenAI-compatible provider | Live |
| Offline deterministic provider (for CI and demos) | Live |
| Additional output formats (PDF, DOCX) | v0.2 |
| Multi-report trend analysis (`qopilot compare`) | v0.3 |

## Quickstart

```bash
pip install qopilot

# Either provider works; Qopilot picks the first one it finds
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...

# Recommend checks for a client system
qopilot author --input examples/acme-system.md --out acme-recs.md

# Interpret an aigrc report
qopilot interpret --report aigrc-report.json --out acme-narrative.md
```

Offline (no API calls, deterministic):

```bash
qopilot author --input examples/acme-system.md --offline
qopilot interpret --report aigrc-report.json --offline
```

## How `author` works

Input: a plain-English markdown file describing the client's AI system. Example:

```markdown
# Acme FinTech chatbot

A customer service assistant for Acme, a 150-person lending company in Ontario.
Built on GPT-4o. Answers product questions. Handles account lookups via a
tool-use integration with the core banking API. Does not provide financial
advice. Regulated under OSFI E-23. European customers pending.
```

Qopilot reads that, consults the aigrc check catalogue and regulatory mappings, and produces a recommendations document with prioritised checks, the regulatory controls each one satisfies, and rationale tied to the client's stated context.

## How `interpret` works

Input: the JSON report produced by `aigrc check ... --report-json report.json`.

Qopilot reads the structured findings, the regulatory mappings, and the target responses, and produces an audit narrative containing:

1. Executive summary (three sentences for a non-technical reader)
2. Material findings grouped by attack class
3. Regulatory traceability matrix (which controls are affected)
4. Prioritised remediation guidance
5. Recommended next engagement (if applicable)

The output is markdown. The same content can be pasted into Google Docs, exported to PDF, or included in a Tier 1 or Tier 2 engagement binder.

## Architecture

```
qopilot/
  core/
    llm.py       Provider abstraction (Anthropic, OpenAI-compatible, offline)
    prompts/     Versioned prompt templates as text files
    schemas.py   Pydantic output schemas for structured generation
  author/        Reads system description, produces check recommendations
  interpret/     Reads aigrc report, produces business narrative
  cli.py         typer CLI
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design decisions.

## Data handling

Qopilot sends the content of the input file (system description or aigrc report) to your configured LLM provider. By default it sends nothing else. The tool never phones home, never collects telemetry, and never retains input data after the command exits.

For environments where no data may leave the client network, use `--offline`. The offline mode uses a deterministic template-based generator. The output is less polished than the LLM version but is sufficient for engineering review and internal drafts.

## Contributing

Early-stage project. Issues and discussion welcome. Please redact client data from any reports you share in issues.

## License

MIT. See [LICENSE](LICENSE).

## About

Qopilot is the AI assistance layer for the Connect Smart Consulting AI assurance stack. Together, aigrc (evidence) and Qopilot (narrative) deliver audit-ready assurance outputs at a price point Ontario SMEs can actually afford.
