"""Tests for Qopilot - offline only to avoid API calls in CI."""

import json
from pathlib import Path

from qopilot.author import render_markdown as render_author_md
from qopilot.author import run as run_author
from qopilot.core import OfflineProvider, autodetect_provider
from qopilot.interpret import render_markdown as render_interpret_md
from qopilot.interpret import run as run_interpret


SAMPLE_DESC = """
A GPT-4o customer service bot for an Ontario lending company. Handles
product questions about loans. Integrates with banking API for account lookups.
Expanding to EU in Q3. Handles customer PII.
"""


def test_autodetect_offline():
    p = autodetect_provider(offline=True)
    assert p.name == "offline"


def test_author_offline_runs():
    provider = OfflineProvider()
    result = run_author(SAMPLE_DESC, provider)
    assert len(result.recommended_checks) >= 1
    ids = [r.check_id for r in result.recommended_checks]
    assert "prompt-injection" in ids


def test_author_offline_flags_pii_when_mentioned():
    provider = OfflineProvider()
    result = run_author(SAMPLE_DESC, provider)
    ids = [r.check_id for r in result.recommended_checks]
    assert "pii-leakage" in ids


def test_author_offline_includes_eu_scope():
    provider = OfflineProvider()
    result = run_author(SAMPLE_DESC, provider)
    assert "EU AI Act" in result.regulatory_scope


def test_author_markdown_renders():
    provider = OfflineProvider()
    result = run_author(SAMPLE_DESC, provider)
    md = render_author_md(result)
    assert "# Qopilot: recommended aigrc checks" in md
    assert "prompt-injection" in md


def test_interpret_offline_with_partial_report():
    report = {
        "check_id": "prompt-injection",
        "check_version": "0.1.0",
        "target": "mock://moderate",
        "started_at": "2026-04-23T00:00:00+00:00",
        "finished_at": "2026-04-23T00:00:10+00:00",
        "frameworks": [
            {"framework": "NIST AI RMF", "control_id": "MEASURE 2.7", "title": "Security"},
            {"framework": "OWASP LLM Top 10", "control_id": "LLM01:2025", "title": "Prompt Injection"},
        ],
        "payloads": [
            {"payload_id": "pi-001", "label": "Direct", "technique": "direct_override",
             "outcome": "FAIL", "evidence": "canary leaked", "target_response": "x", "elapsed_ms": 10},
            {"payload_id": "pi-002", "label": "Base64", "technique": "encoded_payload",
             "outcome": "FAIL", "evidence": "decoded", "target_response": "x", "elapsed_ms": 10},
            {"payload_id": "pi-003", "label": "Role", "technique": "role_confusion",
             "outcome": "PASS", "evidence": "refused", "target_response": "x", "elapsed_ms": 10},
        ],
        "pass_rate": 33.3,
        "summary": "NON-COMPLIANT",
        "offline": True,
    }

    provider = OfflineProvider()
    result = run_interpret(report, provider)
    assert len(result.findings) > 0
    assert "NON-COMPLIANT" in result.regulatory_traceability["NIST AI RMF MEASURE 2.7"]
    md = render_interpret_md(result, report)
    assert "Executive summary" in md
    assert "NIST AI RMF MEASURE 2.7" in md


def test_interpret_offline_with_compliant_report():
    report = {
        "check_id": "prompt-injection",
        "check_version": "0.1.0",
        "target": "mock://strict",
        "started_at": "2026-04-23T00:00:00+00:00",
        "finished_at": "2026-04-23T00:00:10+00:00",
        "frameworks": [
            {"framework": "NIST AI RMF", "control_id": "MEASURE 2.7", "title": "Security"},
        ],
        "payloads": [
            {"payload_id": f"p-{i}", "label": f"p{i}", "technique": "direct_override",
             "outcome": "PASS", "evidence": "refused", "target_response": "x", "elapsed_ms": 10}
            for i in range(18)
        ],
        "pass_rate": 100.0,
        "summary": "COMPLIANT",
        "offline": True,
    }
    provider = OfflineProvider()
    result = run_interpret(report, provider)
    assert len(result.findings) == 0
    assert "COMPLIANT" in result.regulatory_traceability["NIST AI RMF MEASURE 2.7"]
