from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from app.prompts import build_system_prompt, wrap_evidence
from app.schemas import ChatRequest, ChatResponse
from app.services.case_store import case_store
from app.services.llm_client import LLMError, chat_completion

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    case = case_store.get(req.case_id)
    if case is None:
        raise HTTPException(
            status_code=404,
            detail="This case is no longer available (it may have expired). Please start a new investigation.",
        )
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    system_prompt = build_system_prompt(language=req.language, for_chat=True)

    grounding = (
        "Original evidence for this case:\n"
        + wrap_evidence(case.evidence_context)
        + "\n\nCurrent investigation result (already established, do not contradict "
        "without clear reason):\n"
        + json.dumps(case.result_json, ensure_ascii=False, indent=2)
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": grounding})
    messages.append({"role": "assistant", "content": "Understood. I have the case context. Ask your question."})
    for turn in case.history:
        messages.append(turn)
    messages.append({"role": "user", "content": req.message})

    try:
        reply = await chat_completion(messages, temperature=0.3, max_tokens=1500)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    case_store.append_turn(req.case_id, "user", req.message)
    case_store.append_turn(req.case_id, "assistant", reply)

    return ChatResponse(case_id=req.case_id, reply=reply)
