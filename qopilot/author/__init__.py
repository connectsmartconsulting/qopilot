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
    if provider.name == "offline":
        return _offline_author(system_description)

    system_prompt = _load_prompt()
    user_prompt = (
        f"Client system description:\n\n{system_description}\n\n"
        "Produce check recommendations as JSON per the schema."
    )
    resp = provider.complete(system=system_prompt, user=user_prompt, max_tokens=1500)

    try:
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        data = json.loads(text)
        return AuthorOutput(**data)
    except Exception:
        return _offline_author(system_description)


def _offline_author(description: str) -> AuthorOutput:
    lowered = description.lower()

    # Detect verticals
    is_telecom = any(k in lowered for k in ("telecom", "carrier", "crtc", "3gpp", "noc", "network"))
    is_fintech = any(k in lowered for k in ("fintech", "bank", "lending", "osfi", "financial", "fintrac", "kyc"))
    is_agentic = any(k in lowered for k in ("agent", "agentic", "autonomous", "tool call", "multi-step", "workflow"))
    is_article50 = any(k in lowered for k in ("eu ai act", "article 50", "transparency", "customer-facing"))
    is_sb205 = any(k in lowered for k in ("colorado", "sb205", "high-risk ai"))

    recs: list[RecommendedCheck] = [
        RecommendedCheck(
            check_id="prompt-injection",
            priority="high",
            aigrc_status="live",
            regulatory_rationale=(
                "NIST AI RMF MEASURE 2.6 and 2.7 require validation of safety and security. "
                "EU AI Act Article 15 requires robustness against attempts to alter outputs. "
                "OWASP LLM01:2025 is the canonical prompt injection control. "
                "AGCP RG-3 (CR-036 to CR-047) specifies input validation governance trace requirements."
            ),
            client_context_rationale=(
                "The system exposes an LLM to user input — the primary prompt injection attack surface. "
                "Running this check produces governance traces suitable for a NIST AI RMF MEASURE "
                "evidence file, EU AI Act compliance binder, or OSFI E-23 model validation record."
            ),
        )
    ]

    recs.append(
        RecommendedCheck(
            check_id="pii-leakage",
            priority="high",
            aigrc_status="live",
            regulatory_rationale=(
                "NIST AI RMF MEASURE 2.10 (privacy risk); OWASP LLM02:2025 (sensitive information "
                "disclosure); PIPEDA Principle 4.7 (safeguards); EU AI Act Article 10 (data governance). "
                "AGCP RG-6 (CR-062 to CR-069) specifies data governance trace requirements."
                + (" OSFI E-23: PII leakage validation is a required component of model risk management." if is_fintech else "")
                + (" Colorado SB205: PII controls are mandatory for high-risk AI systems." if is_sb205 else "")
            ),
            client_context_rationale=(
                "The system handles or may expose user data. PII leakage testing validates that "
                "the system does not disclose personally identifiable information under adversarial conditions."
            ),
        )
    )

    if is_agentic:
        recs.append(
            RecommendedCheck(
                check_id="agentic-boundary",
                priority="high",
                aigrc_status="planned",
                regulatory_rationale=(
                    "AGCP RG-7 (CR-070 to CR-072) specifies context preservation, downstream agent "
                    "context integrity, and cross-domain delegation boundary requirements for agentic systems. "
                    "AGCP CR-078 requires determinism under non-deterministic agent inputs. "
                    "NIST AI RMF GOVERN 1.7 requires human oversight of autonomous AI actions."
                ),
                client_context_rationale=(
                    "The system uses an agentic architecture with autonomous decision-making. "
                    "Agentic boundary checks validate that the agent stays within its defined action space, "
                    "preserves context across handoffs, and does not exhibit goal drift across multi-step runs. "
                    "Scheduled for aigrc v0.2 — available Q3 2026."
                ),
            )
        )

    if any(k in lowered for k in ("scope", "off-topic", "customer service", "product questions")):
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
                    "The system is scoped to specific domains. Topic boundary enforcement "
                    "should be validated once available in aigrc v0.2."
                ),
            )
        )

    scope = ["NIST AI RMF", "OWASP LLM Top 10", "AGCP"]
    if is_telecom:
        scope.extend(["CRTC Consumer Protection", "EU AI Act Article 50", "ETSI GR SAI 002", "3GPP TS 28.105"])
    if is_fintech:
        scope.extend(["OSFI E-23", "PIPEDA", "FINTRAC"])
    if is_article50 and "EU AI Act Article 50" not in scope:
        scope.append("EU AI Act Article 50")
    if is_sb205:
        scope.append("Colorado SB205 AI Act")
    if any(k in lowered for k in ("eu", "europe", "european")):
        if "EU AI Act" not in scope:
            scope.append("EU AI Act")
    if any(k in lowered for k in ("iso", "42001", "management system")):
        scope.append("ISO/IEC 42001")

    caveats = []
    if is_agentic:
        caveats.append(
            "Agentic boundary checks (AGCP RG-7, CR-070 to CR-072) are planned for aigrc v0.2 — Q3 2026. "
            "Current engagement covers prompt injection and PII leakage checks against the agentic system's "
            "LLM interface. Full agentic loop validation requires v0.2."
        )
    if is_article50:
        caveats.append(
            "EU AI Act Article 50 enforcement date is August 2, 2026. "
            "Remediation and re-validation should be completed before that date."
        )

    return AuthorOutput(
        summary=(
            "The described system is an LLM-based application "
            + ("with agentic capabilities " if is_agentic else "")
            + "exposing natural-language input to users. "
            + ("Primary risks include prompt injection, PII leakage, agentic goal drift, and context integrity. "
               if is_agentic else "Primary risks include prompt injection, system-prompt leakage, and PII disclosure. ")
            + ("AGCP RG-3 and RG-6 are directly applicable. "
               + ("AGCP RG-7 applies to agentic behaviour validation. " if is_agentic else ""))
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
        "*Generated by Qopilot v0.2.0. This is an engineering recommendation. "
        "Final engagement scoping remains with Connect Smart Consulting and the client.*"
    )
    return "\n".join(lines)
