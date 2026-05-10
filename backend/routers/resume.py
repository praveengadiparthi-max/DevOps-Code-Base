import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from models.schemas import TailorResponse, TailorTextRequest
from services.claude_service import tailor_resume
from services.parser import parse_resume
from services.pdf_generator import generate_pdf

router = APIRouter(prefix="/api")

# token -> (pdf_bytes, expiry_unix_timestamp)
pdf_store: dict[str, tuple[bytes, float]] = {}

TOKEN_TTL_SECONDS = 600  # 10 minutes


def _store_pdf(pdf_bytes: bytes) -> str:
    token = str(uuid.uuid4())
    pdf_store[token] = (pdf_bytes, time.time() + TOKEN_TTL_SECONDS)
    return token


def _purge_expired():
    now = time.time()
    expired = [t for t, (_, exp) in pdf_store.items() if now > exp]
    for t in expired:
        pdf_store.pop(t, None)


@router.post("/tailor/upload", response_model=TailorResponse)
async def tailor_from_upload(
    file: UploadFile = File(...),
    job_description: str = Form(..., min_length=20, max_length=20000),
):
    file_bytes = await file.read()
    resume_text = parse_resume(file_bytes, file.filename or "", file.content_type or "")
    structured = tailor_resume(resume_text, job_description)
    pdf_bytes = generate_pdf(structured)
    _purge_expired()
    token = _store_pdf(pdf_bytes)
    return TailorResponse(message="Resume tailored successfully", download_token=token)


@router.post("/tailor/text", response_model=TailorResponse)
async def tailor_from_text(body: TailorTextRequest):
    structured = tailor_resume(body.resume_text, body.job_description)
    pdf_bytes = generate_pdf(structured)
    _purge_expired()
    token = _store_pdf(pdf_bytes)
    return TailorResponse(message="Resume tailored successfully", download_token=token)


@router.get("/download/{token}")
async def download_pdf(token: str):
    entry = pdf_store.get(token)
    if not entry:
        raise HTTPException(status_code=404, detail="Download token not found or already used.")
    pdf_bytes, expiry = entry
    if time.time() > expiry:
        pdf_store.pop(token, None)
        raise HTTPException(status_code=410, detail="Download link has expired. Please tailor again.")
    pdf_store.pop(token, None)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="tailored_resume.pdf"'},
    )
