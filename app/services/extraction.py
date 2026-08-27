"""
Safe, read-only extraction of evidence from uploaded files.

Hard rule (Agents.md section 8 / PRD section 8): a file is NEVER executed or
opened as a program. PDFs are parsed only for their text layer, images are
only validated and re-encoded as base64 for a vision-capable model, and all
other supported types are treated as plain text.
"""
from __future__ import annotations

import base64
import io
from dataclasses import dataclass

from pypdf import PdfReader
from PIL import Image, UnidentifiedImageError

from app.config import settings


class ExtractionError(Exception):
    pass


@dataclass
class ExtractedFile:
    filename: str
    kind: str  # "text" | "image" | "pdf"
    text: str | None = None
    image_data_url: str | None = None
    truncated: bool = False


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def extract_pdf(filename: str, raw: bytes) -> ExtractedFile:
    try:
        reader = PdfReader(io.BytesIO(raw))
    except Exception as exc:  # noqa: BLE001 - surfaced as a safe user-facing error
        raise ExtractionError(f"Could not read PDF '{filename}': {exc}") from exc

    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")
        except Exception:
            raise ExtractionError(
                f"PDF '{filename}' is password-protected and could not be read."
            )

    chunks = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001 - a single bad page shouldn't fail the whole doc
            continue

    text = "\n".join(chunks).strip()
    if not text:
        raise ExtractionError(
            f"No extractable text found in PDF '{filename}' (it may be a scanned image). "
            "Try uploading a screenshot of the relevant pages instead."
        )
    text, truncated = _truncate(text, settings.MAX_PDF_CHARS)
    return ExtractedFile(filename=filename, kind="pdf", text=text, truncated=truncated)


def extract_image(filename: str, raw: bytes, mime_type: str) -> ExtractedFile:
    try:
        img = Image.open(io.BytesIO(raw))
        img.verify()
    except (UnidentifiedImageError, Exception) as exc:  # noqa: BLE001
        raise ExtractionError(f"'{filename}' is not a valid/readable image: {exc}") from exc

    # Re-open after verify() (which invalidates the file pointer), and
    # re-encode through Pillow so we never forward the original bytes verbatim.
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((1600, 1600))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    data_url = f"data:image/jpeg;base64,{b64}"
    return ExtractedFile(filename=filename, kind="image", image_data_url=data_url)


def extract_text(filename: str, raw: bytes) -> ExtractedFile:
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        raise ExtractionError(f"Could not read '{filename}' as text: {exc}") from exc
    text, truncated = _truncate(text, settings.MAX_TEXT_EVIDENCE_CHARS)
    return ExtractedFile(filename=filename, kind="text", text=text, truncated=truncated)


def extract_file(filename: str, raw: bytes, content_type: str | None) -> ExtractedFile:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ExtractionError(f"File type '{ext or 'unknown'}' is not supported.")
    if len(raw) > settings.MAX_UPLOAD_BYTES:
        raise ExtractionError(
            f"'{filename}' exceeds the {settings.MAX_UPLOAD_MB:.0f}MB upload limit."
        )
    if ext == ".pdf":
        return extract_pdf(filename, raw)
    if ext in settings.ALLOWED_IMAGE_EXTENSIONS:
        return extract_image(filename, raw, content_type or "image/*")
    return extract_text(filename, raw)
