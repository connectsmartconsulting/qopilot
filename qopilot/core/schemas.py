"""Pydantic schemas for structured Qopilot outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendedCheck(BaseModel):
    check_id: str
    priority: str = Field(description="high | medium | low")
    aigrc_status: str = Field(description="live | planned")
    regulatory_rationale: str
    client_context_rationale: str


class AuthorOutput(BaseModel):
    summary: str
    regulatory_scope: list[str]
    recommended_checks: list[RecommendedCheck]
    caveats: list[str] = []


class Finding(BaseModel):
    category: str
    severity: str
    description: str
    affected_controls: list[str]
    remediation: str


class InterpretOutput(BaseModel):
    executive_summary: str
    findings: list[Finding]
    regulatory_traceability: dict[str, str]
    next_engagement: str
