# Changelog

## [0.1.0] - 2026-04-23

### Added
- Initial release.
- `qopilot author` command: reads plain-English system description and recommends aigrc checks with regulatory rationale.
- `qopilot interpret` command: reads aigrc JSON evidence report and produces business-language audit narrative with prioritised remediation.
- Provider abstraction supporting Anthropic API, OpenAI-compatible endpoints, and deterministic offline mode.
- Versioned prompt templates stored as plain text files under `qopilot/core/prompts/`.
- Pydantic output schemas for both author and interpret flows.
- Offline deterministic renderers for CI, demos, and air-gapped deployments.
- GitHub Actions CI running pytest and ruff on Python 3.10, 3.11, 3.12.
