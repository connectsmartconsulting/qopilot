# Architecture

## Design principles

Four principles drawn from two decades of quality engineering practice:

1. **Fail explicitly, never silently.** Every failure path (missing API key, malformed report, model returns garbage) surfaces a clear error. Offline fallback exists precisely so that no silent no-op is ever acceptable.
2. **Reproducible given the same input and model.** Temperature defaults to 0. Structured output schemas. Versioned prompt templates.
3. **Human-readable and machine-readable in parallel.** The structured Pydantic output is serializable; the rendered markdown is audit-ready.
4. **CI-native by default.** No hosted service. Input and output are files. The tool runs in any GitHub Actions, GitLab, or Jenkins pipeline.

## Separation from aigrc

aigrc produces deterministic evidence. Qopilot produces narrative and recommendations. Keeping them separate:

- Lets aigrc remain fully deterministic for audit defensibility.
- Lets clients with strict data-residency requirements run aigrc without invoking any external model.
- Makes the cost model transparent: aigrc is free in compute terms, Qopilot has per-call LLM cost.
- Preserves clear responsibility boundaries: evidence is execution, narrative is judgement.

## Provider abstraction

Three providers:

- **Anthropic** (via /v1/messages) - preferred when `ANTHROPIC_API_KEY` is set
- **OpenAI-compatible** (via /v1/chat/completions) - works with OpenAI, Azure OpenAI, vLLM, local Ollama
- **Offline** - deterministic template-based generator

Autodetection picks the first available in that order. The offline provider is not a degraded mode: it is a deliberate, supported execution path for CI and for clients with air-gapped requirements.

## Prompt templates

Prompts live in `qopilot/core/prompts/` as plain text files, not embedded strings. This is deliberate:

- Prompts can be version-controlled and reviewed like code.
- Non-engineers can read and suggest improvements without touching Python.
- The same prompts can be extracted for evaluation harness testing.

Every prompt enforces a JSON output schema. We parse that JSON into Pydantic models. If parsing fails, we fall back to the offline renderer rather than emit broken output. This is part of the "fail explicitly, never silently" principle.

## Offline renderers

The offline `author` and `interpret` functions are deterministic template generators. They:

- Inspect the input for keyword signals (PII mentions, EU mentions, technique names in the report).
- Apply a severity map based on established attack-class risk rankings.
- Apply a remediation map that provides concrete engineering guidance per technique.

The offline output is less polished than a real LLM response but is sufficient for internal engineering review, for CI integration tests, and for air-gapped deployments. Offline is a first-class path, not a toy.

## What we deliberately do not do

- **No PDF generation in core.** Markdown renders to PDF through any standard tool. Keeping the core text-only keeps dependencies minimal.
- **No DOCX generation.** Same reason.
- **No hosted API.** We ship a CLI.
- **No telemetry.** We never phone home.
- **No per-client fine-tuning.** Prompts are public and versioned in this repository.
