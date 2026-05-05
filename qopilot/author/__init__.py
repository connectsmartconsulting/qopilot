"""Author: reads a system description and recommends aigrc checks."""

from __future__ import annotations

import json
from pathlib import Path

from qopilot.core import (
    AuthorOutput,
    Provider,
    RecommendedCheck,
)

PROMPT_DIR = Path(__file__).parent.parent / "core" / "prompts"


def _load_prompt() -> str:
    return (PROMPT_DIR / "author_system.txt").read_text()


def run(system_description: str, provider: Provider) -> AuthorOutput:
    """Produce check recommendations for a given system description.

    Uses the provider's structured output if available; otherwise falls back
    to the deterministic offline renderer.
    """
    if provider.name == "offline":
        return _offline_author(system_description)

    system_prompt = _load_prompt()
    user_prompt = (
        f"Client system description:\n\n{system_description}\n\n"
        "Produce check recommendations as JSON per the schema."
    )
    resp = provider.complete(system=system_prompt, user=user_prompt, max_tokens=1500)

    try:
        # Best-effort: strip any accidental code fences
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        data = json.loads(text)
        return AuthorOutput(**data)
    except Exception:
        # If the LLM output is not valid JSON, fall back to offline
        return _offline_author(system_description)


def _offline_author(description: str) -> AuthorOutput:
    """Deterministic renderer. Inspects description for common signals and
    always recommends prompt-injection (the one live check), plus flags
    relevant planned checks based on keyword heuristics."""
    lowered = description.lower()

    recs: list[RecommendedCheck] = [
        RecommendedCheck(
            check_id="prompt-injection",
            priority="high",
            aigrc_status="live",
            regulatory_rationale=(
                "NIST AI RMF MEASURE 2.6 and 2.7 require validation of safety and "
                "security. EU AI Act Article 15 requires robustness against attempts "
                "to alter outputs. OWASP LLM01:2025 is the canonical prompt injection "
                "control. This is the only check live in aigrc v0.1 and is foundational "
                "for any LLM-facing system."
            ),
            client_context_rationale=(
                "The system exposes an LLM to user input, which is the attack surface "
                "prompt injection targets. Running this check produces evidence suitable "
                "for an OSFI E-23 or EU AI Act file."
            ),
        )
    ]

    caveats = [
        "aigrc v0.1 has one live check. Additional planned checks are listed but not "
        "yet executable. Design partners should expect v0.2 to cover PII leakage and "
        "topic boundary in Q3 2026."
    ]

    if any(k in lowered for k in ("pii", "personal data", "kyc", "account", "customer data")):
        recs.append(
            RecommendedCheck(
                check_id="pii-leakage",
                priority="high",
                aigrc_status="planned",
                regulatory_rationale=(
                    "NIST AI RMF MEASURE 2.10 (privacy); OWASP LLM02:2025 "
                    "(sensitive information disclosure)."
                ),
                client_context_rationale=(
                    "The system handles customer or account data. PII leakage testing "
                    "is a high-priority follow-on once aigrc v0.2 is available."
                ),
            )
        )

    if any(k in lowered for k in ("scope", "off-topic", "product questions", "customer service")):
        recs.append(
            RecommendedCheck(
                check_id="topic-boundary",
                priority="medium",
                aigrc_status="planned",
                regulatory_rationale=(
                    "NIST AI RMF MEASURE 2.11 (fairness and bias in scope enforcement); "
                    "OWASP LLM10:2025 (unbounded consumption)."
                ),
                client_context_rationale=(
                    "The system is scoped to specific product questions. Topic boundary "
                    "enforcement should be validated once available."
                ),
            )
        )

    scope = ["NIST AI RMF", "OWASP LLM Top 10"]
    if any(k in lowered for k in ("eu", "europe", "european")):
        scope.append("EU AI Act")
    if any(k in lowered for k in ("iso", "management system", "42001")):
        scope.append("ISO/IEC 42001")
    if any(k in lowered for k in ("osfi", "fintech", "bank", "lending", "financial")):
        scope.append("OSFI E-23")

    return AuthorOutput(
        summary=(
            "The described system is an LLM-based application exposing natural-language "
            "input to end users. Primary risks are prompt injection, system-prompt "
            "leakage, and (where applicable) PII disclosure and scope violations."
        ),
        regulatory_scope=scope,
        recommended_checks=recs,
        caveats=caveats,
    )


def render_markdown(output: AuthorOutput) -> str:
    lines = []
    lines.append("# Qopilot: recommended aigrc checks")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(output.summary)
    lines.append("")
    lines.append("## Regulatory scope")
    lines.append("")
    for s in output.regulatory_scope:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Recommended checks")
    lines.append("")
    for i, rec in enumerate(output.recommended_checks, 1):
        status_label = "LIVE" if rec.aigrc_status == "live" else "PLANNED"
        lines.append(f"### {i}. `{rec.check_id}` ({status_label}, priority: {rec.priority})")
        lines.append("")
        lines.append(f"**Regulatory rationale:** {rec.regulatory_rationale}")
        lines.append("")
        lines.append(f"**Client context:** {rec.client_context_rationale}")
        lines.append("")
    if output.caveats:
        lines.append("## Caveats")
        lines.append("")
        for c in output.caveats:
            lines.append(f"- {c}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "*Generated by Qopilot. This is an engineering recommendation. "
        "Final engagement scoping remains with Connect Smart Consulting and the client.*"
    )
    return "\n".join(lines)
