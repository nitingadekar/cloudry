"""PDF tool endpoints."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from src.middleware.captcha import verify_turnstile
from src.services.pdf_service import PDFService

router = APIRouter()
pdf_service = PDFService()


@router.post("/unlock", dependencies=[Depends(verify_turnstile)])
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(default="")):
    """Remove password restrictions from a PDF file.

    If the PDF has owner-only restrictions (print/edit disabled), it can be unlocked without a password.
    If the PDF requires a user password to open, you must provide it.
    """
    content = await file.read()
    result = pdf_service.unlock(content, password)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=unlocked_{file.filename}"},
    )


@router.post("/merge", dependencies=[Depends(verify_turnstile)])
async def merge_pdfs(files: list[UploadFile] = File(...)):
    """Merge multiple PDF files into one."""
    contents = [await f.read() for f in files]
    result = pdf_service.merge(contents)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )


@router.post("/split", dependencies=[Depends(verify_turnstile)])
async def split_pdf(file: UploadFile = File(...), pages: str = Form(...)):
    """Split a PDF by page ranges.

    Pages format: "1-3,5,7-9" — extracts specified pages into a new PDF.
    """
    content = await file.read()
    result = pdf_service.split(content, pages)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=split.pdf"},
    )


@router.post("/to-image", dependencies=[Depends(verify_turnstile)])
async def pdf_to_image(file: UploadFile = File(...), format: str = Form(default="png")):
    """Convert PDF pages to images.

    Returns a ZIP file containing one image per page.
    """
    content = await file.read()
    result = pdf_service.to_images(content, format)
    return StreamingResponse(
        result,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pdf_images.zip"},
    )


@router.post("/watermark", dependencies=[Depends(verify_turnstile)])
async def add_watermark(file: UploadFile = File(...), text: str = Form(...)):
    """Add a text watermark to every page of a PDF."""
    content = await file.read()
    result = pdf_service.add_watermark(content, text)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=watermarked_{file.filename}"},
    )


@router.post("/compress", dependencies=[Depends(verify_turnstile)])
async def compress_pdf(file: UploadFile = File(...)):
    """Compress a PDF to reduce file size."""
    content = await file.read()
    result = pdf_service.compress(content)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"},
    )
