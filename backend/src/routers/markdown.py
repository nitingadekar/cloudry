"""Markdown to PDF conversion endpoints."""

from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse

from src.middleware.captcha import verify_turnstile
from src.services.markdown_service import MarkdownService

router = APIRouter()
markdown_service = MarkdownService()


@router.post("/to-pdf", dependencies=[Depends(verify_turnstile)])
async def markdown_to_pdf(content: str = Form(...), title: str = Form(default="Document")):
    """Convert Markdown text to a styled PDF document."""
    result = markdown_service.to_pdf(content, title)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={title}.pdf"},
    )
