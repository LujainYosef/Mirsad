"""
Pydantic models for Mirsad's request/response contracts.

InvestigationResult mirrors the "Dashboard Output Contract" defined in
Agents.md (section 11) so the LLM's structured JSON output can be validated
before it is trusted and rendered by the frontend.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Verdict = Literal["Safe", "Suspicious", "Malicious", "Inconclusive"]
Severity = Literal["Critical", "High", "Medium", "Low", "Informational"]
Confidence = Literal["High", "Medium", "Low"]


class Evidence(BaseModel):
    label: str = Field(..., description="Short title of the observed fact")
    detail: str = Field(..., description="What was directly observed in the supplied evidence")


class SuspiciousEvent(BaseModel):
    title: str
    description: str
    severity: Optional[Severity] = None
    related_indicators: list[str] = Field(default_factory=list)


class IOC(BaseModel):
    type: str = Field(..., description="e.g. ip, domain, url, hash, email, filename")
    value: str
    context: Optional[str] = None


class TimelineEvent(BaseModel):
    timestamp: Optional[str] = None
    description: str


class Hypothesis(BaseModel):
    statement: str
    requires_validation: str = Field(..., description="What would need to be confirmed")


class InvestigationResult(BaseModel):
    case_summary: str
    verdict: Verdict
    severity: Severity
    severity_reason: str
    confidence: Confidence
    confidence_reason: str
    confirmed_evidence: list[Evidence] = Field(default_factory=list)
    suspicious_events: list[SuspiciousEvent] = Field(default_factory=list)
    iocs: list[IOC] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    next_investigation_steps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    analyst_notes: Optional[str] = None


class InvestigateResponse(BaseModel):
    case_id: str
    result: InvestigationResult
    language: Literal["ar", "en"]
    raw_model_error: Optional[str] = Field(
        default=None,
        description="Set only when the model output could not be validated; the "
        "result field then contains a safe fallback (Inconclusive).",
    )


class ChatRequest(BaseModel):
    case_id: str
    message: str
    language: Literal["ar", "en"] = "ar"


class ChatResponse(BaseModel):
    case_id: str
    reply: str
