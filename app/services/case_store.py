"""
In-memory storage for investigation cases.

MVP scope: no database. Each case holds the evidence summary that was
investigated and the resulting dashboard, plus a bounded chat history, so
follow-up chat stays grounded in the original evidence (Agents.md section 14)
without re-uploading files on every message.

Note: state is lost on process restart (e.g. Render redeploy). This is
acceptable for an MVP; see README "Future Improvements" for persistence.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from app.config import settings


@dataclass
class Case:
    case_id: str
    language: str
    evidence_context: str  # condensed, reusable description of the evidence for chat grounding
    result_json: dict
    created_at: float = field(default_factory=time.time)
    history: list[dict] = field(default_factory=list)  # [{"role": "user"/"assistant", "content": str}]


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, Case] = {}

    def _sweep_expired(self) -> None:
        now = time.time()
        expired = [
            cid for cid, c in self._cases.items()
            if now - c.created_at > settings.CASE_TTL_SECONDS
        ]
        for cid in expired:
            self._cases.pop(cid, None)

    def create(self, *, language: str, evidence_context: str, result_json: dict) -> Case:
        self._sweep_expired()
        case = Case(
            case_id=str(uuid.uuid4()),
            language=language,
            evidence_context=evidence_context,
            result_json=result_json,
        )
        self._cases[case.case_id] = case
        return case

    def get(self, case_id: str) -> Case | None:
        self._sweep_expired()
        return self._cases.get(case_id)

    def append_turn(self, case_id: str, role: str, content: str) -> None:
        case = self._cases.get(case_id)
        if not case:
            return
        case.history.append({"role": role, "content": content})
        # Keep history bounded.
        max_messages = settings.MAX_CHAT_HISTORY_TURNS * 2
        if len(case.history) > max_messages:
            case.history = case.history[-max_messages:]


case_store = CaseStore()
