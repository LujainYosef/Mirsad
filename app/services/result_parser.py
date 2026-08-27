"""
Turns raw LLM text output into a validated InvestigationResult.

Never trusts the raw string directly: strips accidental code fences, parses
JSON defensively, and validates against the Pydantic schema. If anything
fails, returns a safe "Inconclusive" fallback instead of surfacing malformed
or partially-trusted content to the frontend (PRD section 9 / Agents.md
section 16 — never present false certainty, never render unsanitized output).
"""
from __future__ import annotations

import json
import re

from pydantic import ValidationError

from app.schemas import InvestigationResult

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = _FENCE_RE.sub("", text)
    return text.strip()


def _extract_json_object(text: str) -> str:
    """Best-effort: grab the first {...} block if there's stray text around it."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start : end + 1]


def parse_investigation_result(raw_text: str, *, language: str) -> tuple[InvestigationResult, str | None]:
    cleaned = _extract_json_object(_strip_fences(raw_text))
    try:
        data = json.loads(cleaned)
        result = InvestigationResult.model_validate(data)
        return result, None
    except (json.JSONDecodeError, ValidationError) as exc:
        fallback = _fallback_result(language)
        return fallback, str(exc)


def _fallback_result(language: str) -> InvestigationResult:
    if language == "ar":
        return InvestigationResult(
            case_summary="تعذّر التحقق من مخرجات النموذج بصيغة منظّمة لهذه الحالة.",
            verdict="Inconclusive",
            severity="Informational",
            severity_reason="لم يتم إسناد شدة لأن المخرجات لم تجتز التحقق من الصحة.",
            confidence="Low",
            confidence_reason="فشل تحليل استجابة النموذج، لذا لا يمكن الوثوق بأي استنتاج تلقائيًا.",
            evidence_gaps=["تعذّر تحليل استجابة النموذج بأمان. يرجى إعادة المحاولة."],
            next_investigation_steps=["أعد إرسال التحقيق، أو قلّل حجم الأدلة المرفوعة وحاول مجددًا."],
            recommendations=["لا تعتمد على هذه النتيجة لاتخاذ قرار أمني."],
        )
    return InvestigationResult(
        case_summary="The model's output for this case could not be validated as structured data.",
        verdict="Inconclusive",
        severity="Informational",
        severity_reason="No severity could be assigned because the output failed validation.",
        confidence="Low",
        confidence_reason="The model response could not be parsed, so no conclusion can be trusted automatically.",
        evidence_gaps=["The model response could not be safely parsed. Please retry."],
        next_investigation_steps=["Resubmit the investigation, or reduce the size of the uploaded evidence and try again."],
        recommendations=["Do not rely on this result for a security decision."],
    )
