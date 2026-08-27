from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import settings
from app.prompts import build_system_prompt, wrap_evidence
from app.schemas import InvestigateResponse
from app.services.case_store import case_store
from app.services.extraction import ExtractedFile, ExtractionError, extract_file
from app.services.llm_client import LLMError, chat_completion
from app.services.result_parser import parse_investigation_result

router = APIRouter()


def _build_evidence_text(text: str | None, url: str | None, files: list[ExtractedFile]) -> str:
    sections: list[str] = []
    if text and text.strip():
        sections.append(f"[Pasted text / log excerpt]\n{text.strip()}")
    if url and url.strip():
        sections.append(f"[Submitted URL]\n{url.strip()}")
    for f in files:
        if f.kind in ("pdf", "text"):
            note = " (truncated to size limit)" if f.truncated else ""
            sections.append(f"[File: {f.filename}]{note}\n{f.text}")
        elif f.kind == "image":
            sections.append(f"[File: {f.filename}] — screenshot/image attached separately for visual review.")
    if not sections:
        sections.append("(No text, URL, or file content was provided.)")
    return "\n\n".join(sections)


@router.post("/api/investigate", response_model=InvestigateResponse)
async def investigate(
    text: str = Form(default=""),
    url: str = Form(default=""),
    language: str = Form(default="ar"),
    files: list[UploadFile] = File(default_factory=list),
):
    if language not in ("ar", "en"):
        language = "ar"

    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum is {settings.MAX_FILES_PER_REQUEST} per investigation.",
        )

    if not text.strip() and not url.strip() and not files:
        raise HTTPException(status_code=400, detail="Provide text, a URL, and/or at least one file.")

    extracted: list[ExtractedFile] = []
    for upload in files:
        raw = await upload.read()
        try:
            extracted.append(extract_file(upload.filename or "upload", raw, upload.content_type))
        except ExtractionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    evidence_text = _build_evidence_text(text, url, extracted)

    system_prompt = build_system_prompt(language=language, for_chat=False)

    user_content: list[dict] = [
        {"type": "text", "text": wrap_evidence(evidence_text)}
    ]
    for f in extracted:
        if f.kind == "image" and f.image_data_url:
            user_content.append({"type": "image_url", "image_url": {"url": f.image_data_url}})

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    try:
        raw_output = await chat_completion(messages, temperature=0.15, max_tokens=4500)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    result, parse_error = parse_investigation_result(raw_output, language=language)

    # Condensed context reused for follow-up chat (keeps chat calls small).
    evidence_context = evidence_text
    if len(evidence_context) > 6000:
        evidence_context = evidence_context[:6000] + "\n...(truncated for chat context)"

    case = case_store.create(
        language=language,
        evidence_context=evidence_context,
        result_json=result.model_dump(),
    )

    return JSONResponse(
        InvestigateResponse(
            case_id=case.case_id,
            result=result,
            language=language,  # type: ignore[arg-type]
            raw_model_error=parse_error,
        ).model_dump()
    )
